from PySide6 import QtCore

settings = QtCore.QSettings("config.ini", QtCore.QSettings.IniFormat)


# Default directories
settings.setValue("dir/last_sigmf_dir", ".")
settings.setValue("dir/last_digitalrf_dir", ".")
settings.setValue("dir/last_onnx_inference_dir", ".")

# Length of each segment
settings.setValue("spectrogram/nperseg", None)
# Desired window to use
settings.setValue("spectrogram/window", 'tukey')
# Number of points to overlap between segments
settings.setValue("spectrogram/noverlap", None)
# Length of the FFT used, if a zero padded FFT is desired. If None, the FFT length is nperseg
settings.setValue("spectrogram/nttf", None)


settings.setValue("automatic_annotations/dt",  int(2**12))
settings.setValue("automatic_annotations/threshold_t", -20)
settings.setValue("automatic_annotations/threshold_f", -30)
settings.setValue("automatic_annotations/threshold_mc",  1e-2)

settings.setValue("visualization/colormap", 0)
settings.setValue("visualization/colormaps",
                  [
                      [(38, 70, 83), (42, 157, 143), (233, 196, 106), (244, 162, 97), (231, 111, 81)],
                      []
                  ])

settings.sync()

print(settings.fileName())
