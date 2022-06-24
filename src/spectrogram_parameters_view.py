from PySide6 import QtCore, QtWidgets


class SpectrogramParametersView(QtWidgets.QGroupBox):

    update_signal = QtCore.Signal(int, str, int, int)

    WINDOWS = [
        "boxcar",
        "triang",
        "blackman",
        "hamming",
        "hann",
        "bartlett",
        "flattop",
        "parzen",
        "bohman",
        "blackmanharris",
        "nuttall",
        "barthann",
        "kaiser",    # needs beta
        "gaussian",  # needs standard deviation
        "general_gaussian", # needs power, width
        "dpss",      # needs normalized half-bandwidth
        "chebwin",   # needs attenuation
        "exponential", # needs center, decay scale
        "tukey",     # needs taperfraction
        "taylor"     # needs number of constant sidelobes, sidelobe level
     ]

    def __init__(self, parent=None, nperseg: int = 0, window: str = 'tukey', noverlap: int = 0, nfft: int = 0):

        super().__init__(parent=parent)

        self.nperseg = 0 if not nperseg else nperseg
        self.window  = window
        self.noverlap = 0 if not noverlap else noverlap
        self.nfft =  0 if not nfft else nfft

        self.__setupUI()

    def __setupUI(self):

        self.setTitle("Spectrogram parameters")

        vertical_layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()

        self.spectrogram_segment_length_label = QtWidgets.QLabel("Segment lenght")
        self.spectrogram_segment_length_spinbox = QtWidgets.QSpinBox(self)
        self.spectrogram_segment_length_spinbox.setMaximum(2**20)
        self.spectrogram_segment_length_spinbox.setValue(self.nperseg)

        form_layout.insertRow(0, self.spectrogram_segment_length_label, self.spectrogram_segment_length_spinbox)

        self.spectrogram_window_label = QtWidgets.QLabel("Window")
        self.spectrogram_window_dropbox = QtWidgets.QComboBox(self)

        for window in self.WINDOWS:
            self.spectrogram_window_dropbox.addItem(window)

        self.spectrogram_window_dropbox.setDisabled(True)

        self.spectrogram_window_dropbox.setCurrentText(self.window)

        form_layout.insertRow(1, self.spectrogram_window_label, self.spectrogram_window_dropbox)

        self.spectrogram_overlap_label = QtWidgets.QLabel("Overlap")
        self.spectrogram_overlap_spinbox = QtWidgets.QSpinBox(self)
        self.spectrogram_overlap_spinbox.setMaximum(2**20)
        self.spectrogram_overlap_spinbox.setValue(self.noverlap)

        form_layout.insertRow(2, self.spectrogram_overlap_label, self.spectrogram_overlap_spinbox)

        self.spectrogram_nfft_label = QtWidgets.QLabel("NFFT")
        self.spectrogram_nfft_spinbox = QtWidgets.QSpinBox(self)
        self.spectrogram_nfft_spinbox.setMaximum(2**20)
        self.spectrogram_nfft_spinbox.setValue(self.nfft)

        form_layout.insertRow(3, self.spectrogram_nfft_label, self.spectrogram_nfft_spinbox)

        self.update_scene_button = QtWidgets.QPushButton(self)
        self.update_scene_button.setText("Update scene")

        self.update_scene_button.clicked.connect(self.update_scene)

        vertical_layout.addLayout(form_layout)
        vertical_layout.addWidget(self.update_scene_button)

        # TODO: Check default values and its relationship

    @QtCore.Slot()
    def update_scene(self):
        nperseg = self.spectrogram_segment_length_spinbox.value()
        window_idx = self.spectrogram_window_dropbox.currentIndex()
        noverlap = self.spectrogram_overlap_spinbox.value()
        nfft = self.spectrogram_nfft_spinbox.value()

        self.update_signal.emit(nperseg, self.WINDOWS[window_idx], noverlap, nfft)

