from pyqtgraph.Qt import QtCore, QtWidgets

from sigmf_model import SigMFModel


class SigMFMetadataView(QtWidgets.QGroupBox):

    select_capture = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(SigMFMetadataView, self).__init__(parent)

    def set_model(self, model=SigMFModel):
        self.__setupUI(model)

    def __setupUI(self, model: SigMFModel):

        self.setTitle("Metadata")

        vertical_layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()

        samples_count_name_label = QtWidgets.QLabel("Sample count:")
        samples_count_value_label = QtWidgets.QLabel(f"{model.get_sample_count()}")

        form_layout.insertRow(0, samples_count_name_label, samples_count_value_label)

        fs_name_label = QtWidgets.QLabel("Sampling frequency:")
        fs_value_label = QtWidgets.QLabel(f"{model.get_sample_rate()} Hz")

        form_layout.insertRow(1, fs_name_label, fs_value_label)

        vertical_layout.addLayout(form_layout)

        global_author_label = QtWidgets.QLabel("Author:")
        global_author_field = QtWidgets.QLineEdit(self)
        global_author_field.setText(f"{model.get_author()}")
        global_author_field.setEnabled(False)

        form_layout.insertRow(2, global_author_label, global_author_field)

        global_description_label = QtWidgets.QLabel("Description")
        global_description_field = QtWidgets.QTextEdit(self)
        global_description_field.setText(f"{model.get_description()}")
        global_description_field.setEnabled(False)

        form_layout.insertRow(3, global_description_label, global_description_field)

        self.capture_dropbox = QtWidgets.QComboBox()

        for capture_idx in range(len(model)):
            self.capture_dropbox.addItem(f"Capture {capture_idx + 1}")

        self.capture_dropbox.setCurrentIndex(0)

        vertical_layout.addWidget(self.capture_dropbox)

