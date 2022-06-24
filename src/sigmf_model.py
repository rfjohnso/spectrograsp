import logging
import math
from sigmf import sigmffile, SigMFFile

from data_model import DataModel
from annotation import Annotation, AnnotationSource


class SigMFModel(DataModel):

    def __init__(self, filename):

        super(SigMFModel, self).__init__()

        # TODO: Use str or Path but consistently across all models
        self.file_name = filename
        self.sigmf_file = sigmffile.fromarchive(filename)

        self.capture = 0
        self.sample_rate = self.sigmf_file.get_global_field(SigMFFile.SAMPLE_RATE_KEY)

        self.parse_metadata()

    def parse_metadata(self):

        for sigmf_annotation in self.sigmf_file.get_annotations():

            # Mandatory fields transformed to time
            start = sigmf_annotation[SigMFFile.START_INDEX_KEY] / self.sample_rate
            length = sigmf_annotation[SigMFFile.LENGTH_INDEX_KEY] / self.sample_rate
            # Optional fields
            high = sigmf_annotation.get(SigMFFile.FHI_KEY, None)
            low = sigmf_annotation.get(SigMFFile.FLO_KEY, None)
            comment = sigmf_annotation.get(SigMFFile.COMMENT_KEY, None)

            label = sigmf_annotation.get('core:label', None)
            group = sigmf_annotation.get('group', None)

            annotation = Annotation(source=AnnotationSource.FILE,
                                    start=start,
                                    length=length,
                                    high=high,
                                    low=low,
                                    comment=comment,
                                    label=label,
                                    group=group)

            self.annotations.append(annotation)

        # print({a.label for a in self.annotations if a.label})
        for label in {a.label for a in self.annotations if a.label}:
            self.labels.add_label(label)
        for group in {a.group for a in self.annotations if a.group}:
            self.groups.add_group(group)

    def __len__(self):
        return len(self.sigmf_file.get_captures())

    def get_sample_rate(self):
        return self.sample_rate

    def get_sample_count(self):
        return self.sigmf_file.sample_count

    def get_author(self):
        return self.sigmf_file.get_global_field(SigMFFile.AUTHOR_KEY)

    def get_description(self):
        return self.sigmf_file.get_global_field(SigMFFile.DESCRIPTION_KEY)

    def get_format(self):
        return self.sigmf_file.get_global_field(SigMFFile.DATATYPE_KEY)

    def read_samples(self, start=0, count=None):
        start += self.sigmf_file.get_captures()[self.capture].get(SigMFFile.START_INDEX_KEY, 0)
        if not count:
            # If sample count not given, read from start to end of the data
            count = self.sigmf_file.sample_count - start
        return self.sigmf_file.read_samples(start, count, autoscale=False, raw_components=False)

    def get_central_frequency(self, idx=None):
        captures = self.sigmf_file.get_captures()
        if len(captures) > 0:
            # Return value of the capture frequency or 0 if does not exists
            return captures[self.capture if idx is None else idx].get(SigMFFile.FREQUENCY_KEY, 0)
        else:
            # No captures, no central frecuency information assume 0
            logging.warning("SigMF MUST contain a top level capture object")
            return 0

    def read_time(self, start=0, length=None):
        # Calculate the sample for start timestamp
        start_sample = start * self.get_sample_rate()
        if not length:
            sample_count = None
        else:
            sample_count = min(self.time_to_sample(length), self.get_sample_count()-start_sample)

        return self.sigmf_file.read_samples(int(start_sample), int(sample_count))

    def create_sigmf_file(self):
        new_file = SigMFFile(metadata=None,
                             data_file=self.sigmf_file.data_file,
                             global_info=self.sigmf_file.get_global_field())

        for capture in self.captures:
            new_file.add_capture([capture])

        #TODO: Add all annotaions in the model in SigMF format
        for annotation in self.annotations:
            ...


    def save(self, file_name=None):
        """
        Saves SigMFModel to SigMF format
        :param file_name: None if overwrite original file or the file name of new file
        :return:
        """

        # TODO: In order to overwrite annotations we have to access the "protected" metadata
        self.sigmf_file._metadata[SigMFFile.ANNOTATION_KEY] = [
            self.get_sigmf_annotation(annotation) for annotation in sorted(self.annotations, key=lambda a: a.start)
        ]

        if file_name:
            # Save as
            if not file_name.endswith('.sigmf'):
                file_name += ".sigmf"

            self.sigmf_file.archive(file_name)
        else:
            # Save
            self.sigmf_file.archive(self.file_name)

        self._modified = False

    def set_modified_status(self, value):
        if self._modified != value:
            self._modified = value
            self.modified_status.emit(self._modified)

    def get_sigmf_annotation(self, annotation: Annotation):
        """

        :param annotation:
        :return:
        """
        sigmf_annotation =  {
            SigMFFile.START_INDEX_KEY: math.floor(annotation.start * self.get_sample_rate()),
            SigMFFile.LENGTH_INDEX_KEY: math.ceil(annotation.length * self.get_sample_rate()),
            SigMFFile.FHI_KEY: annotation.high,
            SigMFFile.FLO_KEY: annotation.low,
        }

        if annotation.metadata.get('author', None):
            sigmf_annotation[SigMFFile.GENERATOR_KEY] = annotation.metadata['author']
        if annotation.metadata.get('comment', None):
            sigmf_annotation[SigMFFile.COMMENT_KEY] = annotation.metadata['comment']
        if annotation.label:
            # FIXME: annotation label is part of the specification (introduced in 259206243e13f63a1793a07972c3d916863183b8) but not label key in python source so we took it from the scheme
            sigmf_annotation["core:label"] = annotation.label

        return sigmf_annotation