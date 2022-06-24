import logging

from PySide6 import QtCore, QtWidgets

from annotation_plot import AnnotationPlot
from annotation_form import AnnotationForm


class AnnotationDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(AnnotationDialog, self).__init__(parent)

        self.model = None

        self.annotation_plot = AnnotationPlot(self)
        self.annotation_form = AnnotationForm(self)

        self.setupUi()

    def setupUi(self):

        self.setWindowTitle("Annotation")
        self.setMinimumSize(800, 480)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(15)

        right_panel = QtWidgets.QWidget(self)
        right_panel.setLayout(QtWidgets.QVBoxLayout())
        right_panel.setMaximumWidth(275)

        self.show_periodogram_check = QtWidgets.QCheckBox(self)
        self.show_periodogram_check.setText("Show periodogram")
        self.show_periodogram_check.setChecked(False)
        self.show_periodogram_check.stateChanged.connect(self.show_periodogram)

        right_panel.layout().addWidget(self.show_periodogram_check)
        right_panel.layout().addWidget(self.annotation_form)

        right_panel.layout().setContentsMargins(0, 0, 0, 0)

        content_layout = QtWidgets.QHBoxLayout()
        content_layout.addWidget(self.annotation_plot)
        content_layout.addWidget(right_panel)

        content_layout.setStretch(0, 3)
        content_layout.setStretch(1, 1)

        main_layout.addLayout(content_layout)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)

        main_layout.addWidget(self.buttonBox)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setLayout(main_layout)

    def set_model(self, model):
        self.model = model
        self.annotation_form.set_model(self.model)
        self.annotation_plot.set_model(self.model)

    def set_annotation(self, annotation):
        if not self.model:
            raise AttributeError(f"Missing model")
        else:
            self.annotation_plot.set_annotation(annotation)
            self.annotation_form.set_annotation(annotation)

    @QtCore.Slot(int)
    def show_periodogram(self, state):
        self.annotation_plot.show_periodogram(state == QtCore.Qt.Checked)
