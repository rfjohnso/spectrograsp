import logging

from PySide6 import QtCore, QtWidgets

from annotation import Annotation
from data_model import DataModel
from annotation_plot import AnnotationPlot
from annotation_form import AnnotationForm

# from s3re.analyse import estimate_sr, extract_signal_with_resampling, is_multicarrier, is_noise
import s3re.analyse as analyse


class AutomaticAnnotationDialog(QtWidgets.QDialog):

    cancel_automatic_annotation_signal = QtCore.Signal()
    accept_all_automatic_annotation_signal = QtCore.Signal()

    def __init__(self, model: DataModel, parent=None):
        super(AutomaticAnnotationDialog, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.model = model

        self.automatic_annotations = []
        self.current_annotation_index = 0

        self.automatic_annotation_running = True

        self.setupUI()

        self.annotation_form.set_model(self.model)
        self.annotation_plot.set_model(self.model)

        self.setCursor(QtCore.Qt.CursorShape.WaitCursor)

    def setupUI(self):

        self.setWindowTitle("Automatic annotation")
        self.setMinimumSize(1024, 768)
        main_layout = QtWidgets.QVBoxLayout()

        # Top
        top_widget = QtWidgets.QWidget(self)
        top_widget.setLayout(QtWidgets.QHBoxLayout())

        self.annotation_plot = AnnotationPlot(self)
        self.annotation_form = AnnotationForm(self)
        # self.annotation_form = QtWidgets.QWidget(self)

        # Top Right
        top_right_widget = QtWidgets.QWidget(top_widget)
        top_right_widget.setLayout(QtWidgets.QVBoxLayout())
        top_right_widget.layout().setContentsMargins(9, 0, 0, 0)
        top_right_widget.setMaximumWidth(275)

        self.calc_simbol_rate_button = QtWidgets.QPushButton("Calculate symbol rate")
        self.calc_simbol_rate_button.setMinimumSize(QtCore.QSize(0, 30))
        self.calc_simbol_rate_button.clicked.connect(self.calc_symbol_rate)

        self.show_periodogram_check = QtWidgets.QCheckBox("Show periodogram")
        self.show_periodogram_check.stateChanged.connect(self.show_periodogram)

        top_right_widget.layout().addWidget(self.show_periodogram_check)
        top_right_widget.layout().addWidget(self.annotation_form)
        top_right_widget.layout().addSpacerItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        top_right_widget.layout().addWidget(self.calc_simbol_rate_button)

        top_widget.layout().addWidget(self.annotation_plot)
        top_widget.layout().addWidget(top_right_widget)

        # Bottom
        bottom_widget = QtWidgets.QWidget(self)
        bottom_widget.setLayout(QtWidgets.QHBoxLayout())

        self.accept_button = QtWidgets.QPushButton("Accept", parent=self)
        self.accept_all_buttom = QtWidgets.QPushButton("Accept All", parent=self)
        self.reject_button = QtWidgets.QPushButton("Reject", parent=self)
        self.cancel_button = QtWidgets.QPushButton("Cancel", parent=self)

        # self.calc_simbol_rate_button.setDisabled(True)
        self.accept_button.setDisabled(True)
        self.accept_all_buttom.setDisabled(True)
        self.reject_button.setDisabled(True)

        self.calc_simbol_rate_button.setAutoDefault(False)
        self.accept_button.setAutoDefault(False)
        self.accept_all_buttom.setAutoDefault(False)
        self.reject_button.setAutoDefault(False)
        self.cancel_button.setAutoDefault(False)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 0)

        self.progress_label = QtWidgets.QLabel(f"")

        bottom_widget.layout().addWidget(self.progress_bar)
        bottom_widget.layout().addWidget(self.progress_label)
        bottom_widget.layout().addSpacerItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        bottom_widget.layout().addWidget(self.accept_button)
        bottom_widget.layout().addWidget(self.accept_all_buttom)
        bottom_widget.layout().addWidget(self.reject_button)
        bottom_widget.layout().addWidget(self.cancel_button)

        self.accept_button.clicked.connect(self.accept_annotation)
        self.accept_all_buttom.clicked.connect(self.accept_all_annotations)
        self.reject_button.clicked.connect(self.reject_annotation)
        self.cancel_button.clicked.connect(self.cancel_automatic_annotation)

        main_layout.addWidget(top_widget)
        main_layout.addWidget(bottom_widget)

        self.setLayout(main_layout)

    def add_annotation(self, annotation: Annotation):
        # Add annotation to the list of detected annotation
        self.automatic_annotations.append(annotation)

        if len(self.automatic_annotations) == 1:
            # On the first annotation added, show annotation
            self.set_annotation(self.automatic_annotations[0])
            self.setCursor(QtCore.Qt.CursorShape.BusyCursor)

        self.accept_button.setDisabled(False)
        self.reject_button.setDisabled(False)
        self.update_progress()

    def set_annotation(self, annotation: Annotation):
        self.annotation_plot.set_annotation(annotation)
        self.annotation_form.set_annotation(annotation)

    def automatic_annotation_detection_finished(self):
        """
        Update progress representation indicating that the process has finished
        :return:
        """
        if len(self.automatic_annotations) == 0:
            # ended without automatic annotations
            QtWidgets.QMessageBox.information(self, "Automatic annotation", "No annotation found")
            self.accept()
        else:
            self.automatic_annotation_running = False
            self.accept_all_buttom.setDisabled(False)
            self.progress_bar.setMaximum(len(self.automatic_annotations))
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

    def update_progress(self):
        self.progress_label.setText(f"{self.current_annotation_index + 1}/{len(self.automatic_annotations)}")
        self.progress_bar.setValue(self.current_annotation_index+1)

    def next_annotation(self):
        # Move to next annotation
        if self.current_annotation_index == len(self.automatic_annotations) - 1:
            # We have reached the end of the available annotations
            if self.automatic_annotation_running:
                # Wait for new automatic annotations
                self.accept_button.setDisabled(True)
                self.reject_button.setDisabled(True)
            else:
                # Automatic annotation has finished and there will not be more annotations
                self.accept()
        else:
            self.current_annotation_index += 1
            self.set_annotation(self.automatic_annotations[self.current_annotation_index])
            self.update_progress()

    @QtCore.Slot()
    def calc_symbol_rate(self):
        annotation = self.automatic_annotations[self.current_annotation_index]

        logging.debug(f"Calculate symbol rate for annotation from {annotation.start} for {annotation.length}")

        data = self.model.read_time(annotation.start, annotation.length)

        try:
            data_filtered = analyse.extract_signal_with_resampling(data,
                                                           # Normalize frequency between -0.5, 0.5
                                                           annotation.low/self.model.get_sample_rate(),
                                                           annotation.high/self.model.get_sample_rate(),
                                                           False)
            if analyse.is_multicarrier(data_filtered):
                multicarrier_msg = QtWidgets.QMessageBox()
                multicarrier_msg.setIcon(QtWidgets.QMessageBox.Information)
                multicarrier_msg.setWindowTitle("Symbol rate estimation")
                multicarrier_msg.setText("Annotation is detected as multicarrier and symbol rate will not be estimated")
                multicarrier_msg.exec()
            else:
                logging.info("Estimate symbol rate")
                self.setCursor(QtCore.Qt.CursorShape.WaitCursor)
                annotation.metadata['symbol_rate'] = analyse.estimate_sr(data, self.model.get_sample_rate()) * self.model.get_sample_rate()
                annotation.annotation_changed.emit(annotation)
                if self.automatic_annotation_running:
                    self.setCursor(QtCore.Qt.CursorShape.BusyCursor)
                else:
                    self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

        except Exception as error:
            QtWidgets.QMessageBox.critical(self, "Symbol rate error", str(error))

    @QtCore.Slot(int)
    def show_periodogram(self, state):
        self.annotation_plot.show_periodogram(state)

    @QtCore.Slot()
    def accept_annotation(self):
        logging.debug(f"Automatic annotation accepted")

        current_annotation = self.automatic_annotations[self.current_annotation_index]

        if current_annotation.label and current_annotation.label not in self.model.labels.labels:
            res = QtWidgets.QMessageBox.question(self,
                                                 "New label",
                                                 f"Would you like to add {current_annotation.label} to the available labels?")

            if res == QtWidgets.QMessageBox.Yes:
                self.model.labels.add_label(current_annotation.label)
            else:
                pass

        if current_annotation.group and current_annotation.group not in self.model.groups.groups:
            res = QtWidgets.QMessageBox.question(self,
                                                 "New group",
                                                 f"Would you like to add {current_annotation.group} to the available groups?")

            if res == QtWidgets.QMessageBox.Yes:
                self.model.groups.add_group(current_annotation.group)
            else:
                pass

        try:
            self.model.add_annotation(current_annotation)
        except ValueError as error:
            logging.warning(f"Error adding annotation", str(error))
        self.next_annotation()

    @QtCore.Slot()
    def reject_annotation(self):
        logging.debug(f"Automatic annotation rejected")
        self.next_annotation()

    @QtCore.Slot()
    def accept_all_annotations(self):
        logging.debug(f"Accept all automatic annotation")
        for annotation_idx in range(self.current_annotation_index, len(self.automatic_annotations)):
            self.model.add_annotation(self.automatic_annotations[annotation_idx])
        self.accept()
        # self.clean_up()

    @QtCore.Slot()
    def cancel_automatic_annotation(self):
        self.cancel_automatic_annotation_signal.emit()
        self.reject()
        # self.clean_up()

    def clean_up(self):
        self.annotation_plot.deleteLater()
        self.annotation_form.deleteLater()
