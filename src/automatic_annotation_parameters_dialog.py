from PySide6 import QtCore, QtWidgets


class AutomaticAnnotationParametersDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(AutomaticAnnotationParametersDialog, self).__init__(parent)

        settings = QtCore.QSettings("config.ini", QtCore.QSettings.IniFormat)

        settings.beginGroup('automatic_annotations')
        # Analysis step in the time domain (in number of samples).
        #   This values is a trade-off: the larger it is, the better the resolution in the
        #   frequency domain but you lose resolution in the time domain, and vice-versa.
        self.dt = int(settings.value('dt'))
        # Threshold, expressed in dB, used to segment the signal in the time domain.
        self.threshold_t = float(settings.value('threshold_t'))
        # Threshold, expressed in dB, used to segment the spectrum in Bands-Of-Interest.
        self.threshold_f = float(settings.value('threshold_f'))
        # Threshold on 4th moment, used to split single-carrier from multi-carrier signals (and noise).
        self.threshold_mc = float(settings.value('threshold_mc'))

        self.setupGUI()

    def setupGUI(self):

        self.setModal(True)

        self.setWindowTitle("Automatic annotation")

        main_layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()

        self.time_threshold_label = QtWidgets.QLabel("Threshold in time")
        self.time_threshold_spinbox = QtWidgets.QDoubleSpinBox(self)
        self.time_threshold_spinbox.setMaximum(100)
        self.time_threshold_spinbox.setMinimum(-100)
        self.time_threshold_spinbox.setSuffix(" dB")
        self.time_threshold_spinbox.setValue(self.threshold_t)

        self.time_threshold_spinbox.valueChanged.connect(self.update_time_threshold)

        form_layout.insertRow(0, self.time_threshold_label, self.time_threshold_spinbox)

        self.freq_threshold_label = QtWidgets.QLabel("Threshold in freq.")
        self.freq_threshold_spinbox = QtWidgets.QDoubleSpinBox(self)
        self.freq_threshold_spinbox.setMaximum(100)
        self.freq_threshold_spinbox.setMinimum(-100)
        self.freq_threshold_spinbox.setSuffix(" dB")
        self.freq_threshold_spinbox.setValue(self.threshold_f)

        self.freq_threshold_spinbox.valueChanged.connect(self.update_freq_threshold)

        form_layout.insertRow(1, self.freq_threshold_label, self.freq_threshold_spinbox)

        # self.mc_threshold_label = QtWidgets.QLabel("4th moment threshold")
        # self.mc_threshold_spinbox = QtWidgets.QDoubleSpinBox(self)
        # self.mc_threshold_spinbox.setMaximum(1.000)
        # self.mc_threshold_spinbox.setMinimum(0.001)
        #
        # form_layout.insertRow(2, self.mc_threshold_label, self.mc_threshold_spinbox)

        main_layout.addLayout(form_layout)
        main_layout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        action_layout = QtWidgets.QHBoxLayout()

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0,0)
        self.progress_bar.setVisible(False)

        self.calculate_button = QtWidgets.QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.accept)

        action_layout.addWidget(self.progress_bar)
        action_layout.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        action_layout.addWidget(self.calculate_button)

        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)

    @QtCore.Slot(float)
    def update_freq_threshold(self, value):
         self.threshold_f = value

    @QtCore.Slot(float)
    def update_time_threshold(self, value):
        self.threshold_t = value
