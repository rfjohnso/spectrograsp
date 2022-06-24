import logging
import numpy as np

from PySide6 import QtCore, QtWidgets, QtGui

# from s3re.detection import Detection
# from s3re.analyse import time_segmentation

from s3re import detection as detection
from s3re import analyse as analyse

from automatic_annotation_dialog import AutomaticAnnotationDialog
from automatic_annotation_parameters_dialog import AutomaticAnnotationParametersDialog

from data_model import DataModel
from annotation import Annotation, AnnotationSource


class AutomaticAnnotationWorker(QtCore.QThread):

    detection_signal = QtCore.Signal(float, float, float, float)

    def __init__(self, x, dt, threshold_t, threshold_f):

        super().__init__()

        self.x = x
        self.dt = dt
        self.threshold_t = threshold_t
        self.threshold_f = threshold_f

    def run(self) -> None:

        analyse.time_segmentation(self.x,
                                  self.dt,
                                  self.threshold_t,
                                  self.threshold_f,
                                  self.detection_callback,
                                  False)

    def detection_callback(self, x_chunks: np.ndarray, start_sample: int, det: detection.Detection) -> None:
        # self.sleep(1)
        self.detection_signal.emit(det.start_sample,
                                   det.end_sample,
                                   det.get_last_lfreq(),
                                   det.get_last_hfreq())


class AutomaticAnnotation(QtCore.QObject):

    automatic_annotation_detected = QtCore.Signal(object)

    def __init__(self, model: DataModel, parent=None):
        super(AutomaticAnnotation, self).__init__()

        self.model = model

        # Automatic annotation parameters view
        self.automatic_annotation_parameters = AutomaticAnnotationParametersDialog(parent=parent)
        # Annotation user confirmation
        self.automatic_annotation_dialog = AutomaticAnnotationDialog(parent=parent, model=model)

        self.automatic_annotation_dialog.cancel_automatic_annotation_signal.connect(self.stop_automatic_annotation)
        # self.automatic_annotation_dialog.accept_all_automatic_annotation.connect()

    def configure_automatic_annotation(self):
        # Show automatic annotation configuration dialog
        self.automatic_annotation_parameters.exec()
        return self.automatic_annotation_parameters.result()

    def start_automatic_annotation(self):

        # TODO: Optimization for huge
        data = self.model.read_samples()
        # Data needs to be normalized (look up documentation)
        data = data/np.mean(np.abs(data))

        # Initialize worker with automatic annotation parameters
        self.worker = AutomaticAnnotationWorker(data,
                                                self.automatic_annotation_parameters.dt,
                                                self.automatic_annotation_parameters.threshold_t,
                                                self.automatic_annotation_parameters.threshold_f)

        self.worker.detection_signal.connect(self.annotation_found)
        self.worker.finished.connect(self.worker_finished)

        self.worker.start()

        if self.worker.isRunning():
            self.accept_all_automatic_annotations = False
            self.automatic_annotation_dialog.exec()
        else:
            logging.error("Error running automatic annotation")
            QtWidgets.QErrorMessage(self.parent(), "Error running automatic annotation")

    @QtCore.Slot()
    def worker_finished(self):
        # Inform the automatic annotation dialog that the process has finished
        self.automatic_annotation_dialog.automatic_annotation_detection_finished()

    @QtCore.Slot(float, float, float, float)
    def annotation_found(self, start, end, low, high):

        logging.debug(f"Annotation found at [{start}, {end}, {low:3f}, {high:3f}]")

        annotation_start_time = self.model.sample_to_time(start)
        annotation_length_time = self.model.sample_to_time(end - start)

        annotation_high_freq = self.model.get_central_frequency() + self.model.get_sample_rate() * high
        annotation_low_freq = self.model.get_central_frequency() + self.model.get_sample_rate() * low

        automatic_annotation = Annotation(source=AnnotationSource.AUTOMATIC,
                                          start=annotation_start_time, length=annotation_length_time,
                                          high=annotation_high_freq, low=annotation_low_freq,
                                          author="SpectroGrasp",
                                          comment="Automatic annotation")

        if self.automatic_annotation_dialog.result() == QtWidgets.QDialog.Accepted:
            # Add annotation to the model
            self.model.add_annotation(automatic_annotation)
        else:
            # Add annotation to the automatic annotation dialog
            self.automatic_annotation_dialog.add_annotation(automatic_annotation)

    @QtCore.Slot()
    def stop_automatic_annotation(self):
        if self.worker.isRunning():
            logging.info("Automatic annotation canceled  (worker that was running)")
            self.worker.quit()
        else:
            logging.info("Automatic annotation canceled")
