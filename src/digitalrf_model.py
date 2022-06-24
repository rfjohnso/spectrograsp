import logging
import digital_rf as drf

from data_model import DataModel
from annotation import Annotation, AnnotationSource

import shutil
from pathlib import Path


class DigitalRFModel(DataModel):

    METADATA_FOLDER = "spectrogram"

    def __init__(self, channel_properties: str, metadata: str = None):
        """
        :param channel_properties: drf_properties.h5 file (absolute or relative) path
        :param metadata: dmd_properties.h5 file (absolute or relative path)
        """

        super(DigitalRFModel, self).__init__()
        # Make properties path absolute (might raise FileNotFoundError)
        self.channel_path = Path(channel_properties).resolve(strict=True).parent
        self.digitalrf_data = drf.DigitalRFReader(str(self.channel_path.parent))
        self.channel = self.channel_path.stem

        self.sub_channel = 0
        self.parse_metadata(metadata)

    def parse_metadata(self, metadata: str):

        if metadata is None:
            # Empty metadata try to use defaults
            # TODO choose metadata precedence between default folders "metadata" and METADATA_FOLDER
            if self.channel_path.joinpath(self.METADATA_FOLDER).exists():
                self.metadata_path = self.channel_path.joinpath(self.METADATA_FOLDER)
            else:
                self.metadata_path = self.channel_path.joinpath("metadata")
            logging.debug(f"Using default metadata folder {self.channel_path}")
        else:
            self.metadata_path = Path(metadata).resolve().parent
            logging.debug(f"Using metadata folder {self.channel_path}")

        # self.metadata_path = Path(metadata).resolve(strict=True).parent
        try:
            metadata_reader = drf.DigitalMetadataReader(str(self.metadata_path))
        except IOError as error:
            logging.warning(f"Metadata {self.metadata_path} for channel {self.get_channel()} not found")
        else:
            self.annotations.clear()
            self.labels.reset()
            self.groups.reset()

            # Get channel boundaries
            start, end = self.digitalrf_data.get_bounds(self.get_channel())
            # Create an annotation from each read element
            for key, value in metadata_reader.read(start, end).items():
                # Logging possible errors
                # if key != self.time_to_sample(value.get('start')):
                #     logging.warning(f"Mismatch between metadata index ({key}) and annotation start {value.get('start')}")

                # Fixme: Adapt annotation parsing to the right format
                annotation = Annotation(
                    source=AnnotationSource.FILE,
                    start=value.get('start'),
                    length=value.get('length'),
                    high=value.get('high'),
                    low=value.get('low'),
                    author=value.get('author'),
                    comment=value.get('comment'),
                    group=value.get('group', None),
                    symbol_rate=value.get('symbol_rate'),
                    confidence=value.get('confidence'),
                    label=value.get('label', None)
                )
                self.annotations.append(annotation)

           # print({a.label for a in self.annotations if a.label})
            for label in {a.label for a in self.annotations if a.label}:
                self.labels.add_label(label)
            # print({a.group for a in self.annotations if a.group}
            for group in {a.group for a in self.annotations if a.group}:
                self.groups.add_group(group)

    def get_channels(self):
        return self.digitalrf_data.get_channels()

    def get_channel(self):
        return self.channel

    def get_sub_channel(self):
        return self.sub_channel

    def set_sub_channel(self, sub_channel: int):
        properties = self.digitalrf_data.get_properties(self.get_channel())
        if sub_channel < properties["num_subchannels"]:
            self.sub_channel = sub_channel
        else:
            raise ValueError(f"Current channel {self.channel} does not have subchannel {sub_channel}")

    def get_sample_count(self):
        start, end = self.digitalrf_data.get_bounds(self.get_channel())
        return end - start

    def get_sample_rate(self):
        properties = self.digitalrf_data.get_properties(self.get_channel())
        return int(properties["sample_rate_numerator"]/properties["sample_rate_denominator"])

    def get_central_frequency(self, idx=None):
        # TODO: Extract the central frequency from wherever is stored
        return 0

    def read_samples(self, start=None, count=None):
        # Read until the end of the file
        start_sample, end_sample = self.digitalrf_data.get_bounds(self.get_channel())

        if start:
            read_start = start + start_sample
        else:
            read_start = start_sample

        if count:
            read_end = read_start + count
        else:
            # Read until the end of the file
            read_end = end_sample

        samples = self.digitalrf_data.read(read_start, read_end, self.get_channel(), self.get_sub_channel())

        # Get the first (and only) continuous block
        return next(iter(samples.items()))[1]

    def read_time(self, start=0, length=None):

        start_sample = self.time_to_sample(start)

        if length:
            end_sample = start_sample + self.time_to_sample(length)
        else:
            _, end_sample = self.digitalrf_data.get_bounds(self.get_channel())

        samples = self.read_samples(start_sample, end_sample - start_sample)

        return samples

    def save(self, path: str = None):

        if path:
            # Save as
            metadata_dir = Path(path)
        else:
            # Save
            metadata_dir = self.metadata_path

        # Since we cannot overwrite metadata in then DigitalRF python implementation we need to create a new metadata
        # every time we need to save it. Therefore we will follow these steps when saving
        # - We rename old metadata folder to a backup folder
        # - Create new metadata folder
        # - Write metadata folder
        # - If no error, remove backup folder
        # - If error, restore backup folder

        first_sample_index, last_sample_index = self.digitalrf_data.get_bounds(self.get_channel())

        try:
            metadata_backup_dir = Path(str(metadata_dir) + "_bk")

            if metadata_dir.exists():
                metadata_dir.rename(metadata_backup_dir)

            metadata_dir.mkdir(parents=False, exist_ok=True)

            properties = self.digitalrf_data.get_properties(self.get_channel())

            metadata_writer = drf.DigitalMetadataWriter(
                metadata_dir=str(metadata_dir),
                subdir_cadence_secs=properties['subdir_cadence_secs'],
                # Going from miliseconds in the data to seconds in the metadata
                file_cadence_secs=max(round(properties['file_cadence_millisecs']/1000), 1),
                sample_rate_numerator=properties['sample_rate_numerator'],
                sample_rate_denominator=properties['sample_rate_denominator'],
                file_name=self.METADATA_FOLDER
            )

            for annotation in self.annotations:
                # Transform annotation time start to sample index
                annotation_sample_index = self.time_to_sample(annotation.start) + first_sample_index
                metadata_writer.write(samples=annotation_sample_index, data=annotation.to_dict())

        except Exception as error:
            # Something went wrong Restore backup
            logging.error(f"Error saving {metadata_dir}, restoring backup folder {metadata_backup_dir}")
            # Remove current metadata folder
            if metadata_dir.exists():
                shutil.rmtree(metadata_dir)
            # Restore backup if any
            if metadata_backup_dir.exists():
                metadata_backup_dir.rename(metadata_dir)
            raise
        else:
            # No error, clean up backup
            logging.debug(f"No error saving {metadata_dir}, removing backup folder {metadata_backup_dir}")
            if metadata_backup_dir.exists():
                shutil.rmtree(metadata_backup_dir)
            self.metadata_path = metadata_dir
            self._modified = False
