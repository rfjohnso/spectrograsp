from PySide6 import QtCore, QtWidgets

from digitalrf_model import DigitalRFModel


class DigitalRFMetadataView(QtWidgets.QGroupBox):

    select_channel = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(DigitalRFMetadataView, self).__init__(parent)

    def set_model(self, model=DigitalRFModel):
        self.model = model
        self._setupUI()

    def _setupUI(self):

        self.setTitle("Metadata")

        vertical_layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()

        samples_count_name_label = QtWidgets.QLabel("Sample count:")
        samples_count_value_label = QtWidgets.QLabel(f"{self.model.get_sample_count()}")

        fs_name_label = QtWidgets.QLabel("Sampling frequency:")
        fs_value_label = QtWidgets.QLabel(f"{self.model.get_sample_rate()} Hz")

        form_layout.insertRow(0, samples_count_name_label, samples_count_value_label)
        form_layout.insertRow(1, fs_name_label, fs_value_label)

        vertical_layout.addLayout(form_layout)

        self.channels_dropbox = QtWidgets.QComboBox()

        for channel in self.model.get_channels():
            self.channels_dropbox.addItem(f"Channel {channel}")

        self.channels_dropbox.setCurrentText(self.model.get_channel())

        vertical_layout.addWidget(self.channels_dropbox)
