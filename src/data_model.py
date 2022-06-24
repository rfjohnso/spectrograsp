import logging

import numpy as np

from pyqtgraph.Qt import QtCore

from annotation import Annotation
from labels_model import LabelsModel
from groups_model import GroupsModel

class DataModel(QtCore.QObject):

    annotation_added = QtCore.Signal(object)
    annotation_removed = QtCore.Signal(object)
    modified_status = QtCore.Signal(bool)

    def __init__(self):
        # Initalize base class
        super(DataModel, self).__init__()
        # Modified status of the file
        self._modified = False
        # Annotation list, default empty
        self.annotations = []

        self.labels = LabelsModel([])
        self.groups = GroupsModel([])

    def get_sample_rate(self):
        """Abstract method
        Returns the sample rate of the data
        """
        raise NotImplementedError

    def get_central_frequency(self, idx=None):
        """Abstract method
        Returns the central frequency of element idx
        :param idx: Index of the element
        :return: Central frequency in Hz
        """
        raise NotImplementedError

    def get_sample_count(self):
        """Abstract method
        Returns the total sample count
        """
        #TODO Sample count should return the total sample count per dimension (capture, channel)?
        raise NotImplementedError

    def read_samples(self, start=0, count=None):
        raise NotImplementedError

    def read_time(self, start=0, length=None):
        raise NotImplementedError

    def save(self, file: None):
        raise NotImplementedError

    def get_annotation(self, idx):
        """Abstract method
        Returns the annotation with a determined index
        :param idx: Annotation index
        :return: The annotation with index :param idx or None
        """
        return self.annotations[idx]

    def get_selected_annotations(self):
        return [a for a in self.annotations if a.selected]

    def get_selected_annotation_count(self):
        return len(self.get_selected_annotations())

    def get_annotation_idx(self, annotation: Annotation) -> int:
        """
        Returns the index of an annotation
        :param annotation:
        :return:
        """
        return self.annotations.index(annotation)

    def annotation_count(self):
        """
        Returns the number of annotations in the model
        :return: Number of annotations in the model
        """
        return len(self.annotations)

    def add_annotation(self, annotation: Annotation) -> None:
        """ Add the annotation to the model
        :param annotation: Annotation to be added
        :return:
        """
        annotation_rect = QtCore.QRectF(annotation.start, annotation.low, annotation.length, annotation.high)

        for ma in self.annotations:
            model_annotation_rect = QtCore.QRectF(ma.start, ma.low, ma.length, ma.high)

            if annotation_rect == model_annotation_rect:
                logging.warning("Adding duplicated annotation to model is not valid")
                # raise ValueError("Duplicated annotation")

        # Add annotation to the list
        self.annotations.append(annotation)

        # Signal that a new annotation has been added
        self.annotation_added.emit(annotation)

        self._modified = True

    def export_annotations(self, annotation: Annotation, file: str):
        try:
            annotation_data = self.read_time(annotation.start, annotation.length)
            annotation_data.tofile(file)
        except Exception as export_error:
            logging.error(f"Error export annotation {export_error}")
        else:
            logging.info(f"Success exporting annotation")

    # TODO: Check if this the correct place to put selected annotation functionality

    def remove_selected_annotations(self):
        for selected_annotation in self.get_selected_annotations():
            self.remove_annotation(selected_annotation)
            self._modified = True

    def merge_selected_annotations(self):
        selected_annotation = self.get_selected_annotations()
        merged_annotation = Annotation.merge_annotations(selected_annotation)
        self.remove_selected_annotations()
        self.add_annotation(merged_annotation)
        self._modified = True

    def remove_annotation(self, annotation: Annotation) -> None:
        """ Removes annotation from the model
        :param annotation: Annotation to be removed
        :return:
        """
        # Remove annotation to the list
        self.annotations.remove(annotation)
        self.annotation_removed.emit(annotation)
        self._modified = True

    def time_to_sample(self, time: float) -> int:
        """
        Gets the sample index of a time mark
        :param time: Time mark
        :return: Sample of index of the time mark
        """
        return round(time * self.get_sample_rate())

    def sample_to_time(self, sample: int) -> float:
        """
        Gets the time mark of a sample index
        :param sample: Sample index
        :return: Time mark of :param sample
        """
        return sample/self.get_sample_rate()
