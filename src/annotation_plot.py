import numpy as np
import pyqtgraph as pg

from annotation import Annotation
from data_model import DataModel
from annotation_roi import AnnotationROI

from scipy import signal, fftpack

colors = [(38, 70, 83), (42, 157, 143), (233, 196, 106), (244, 162, 97), (231, 111, 81)]


class AnnotationPlot(pg.GraphicsLayoutWidget):

    def __init__(self, parent=None):
        super(AnnotationPlot, self).__init__(parent=parent)

        self.colormap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 5), color=colors)

        self.periodogram_label = self.addLabel(row=1, col=0)
        self.periodogram_plot = self.addPlot(row=2, col=0)

        self.periodogram_plot.setLabel("left", "PSD")
        self.periodogram_plot.setLabel("bottom", "Frequency", units="Hz")

        self.spectrogram_label = self.addLabel(row=3, col=0)
        self.spectrogram_plot  = self.addPlot(row=4,  col=0)

        self.ci.layout.setRowStretchFactor(4, 2)

        self.spectrogram_plot.setLabel("left", "Time", units="s")
        self.spectrogram_plot.setLabel("bottom", "Frequency", units="Hz")

        # self.centralLayout.setContentsMargins(10, 25, 25, 10)
        self.periodogram_plot.setMenuEnabled(enableMenu=False, enableViewBoxMenu=False)
        self.spectrogram_plot.setMenuEnabled(enableMenu=False, enableViewBoxMenu=False)

        self.periodogram_plot.setXLink(self.spectrogram_plot)

        self.periodogram_label.hide()
        self.periodogram_plot.hide()
        self.show_periodogram_ = False

        self.spectrogram_label.hide()

        self.spectrogram_image = pg.ImageItem(lut=self.colormap.getLookupTable())
        self.spectrogram_image.setOpts(axisOrder='col-major')

    def show_periodogram(self, show):
        if show:
            self.show_periodogram_ = True
            self.periodogram_plot.show()
        else:
            self.show_periodogram_ = False
            self.periodogram_plot.hide()

    def set_model(self, model):
        self.model = model

    def set_annotation(self, annotation: Annotation, draw_model_annotations=True):
        self.annotation = annotation

        # Clear all items and add the image back
        self.spectrogram_plot.clear()
        self.spectrogram_plot.addItem(self.spectrogram_image)

        annotation_time_end = annotation.start + annotation.length
        model_total_length = self.model.sample_to_time(self.model.get_sample_count())

        # print(annotation_time_end, annotation.length)

        # Plot boundaries (time) for the annotation plot
        plot_time_start = max(annotation.start - annotation.length, 0)
        plot_time_end = min(annotation_time_end + annotation.length, model_total_length)

        # Read data from model using just plot time boundaries
        plot_data = self.model.read_time(plot_time_start, plot_time_end - plot_time_start)

        # Compute spectrogram
        f, t, sxx = signal.spectrogram(plot_data, fs=self.model.get_sample_rate(), return_onesided=False)

        # Frequency shift for both sides
        f = fftpack.fftshift(f)
        sxx = fftpack.fftshift(sxx, axes=0)

        # Spectrogram log scale
        sxx_log = 10 * np.log10(sxx)

        y = plot_time_start
        h = plot_time_end - plot_time_start

        x = self.model.get_central_frequency() - self.model.get_sample_rate() / 2
        w = self.model.get_sample_rate()

        self.spectrogram_image.setImage(sxx_log, rect=[x, y, w, h])

        self.spectrogram_plot.setLimits(xMin=x, xMax=x + w, yMin=y, yMax=y + h)

        half_sample_length = annotation.length / 2

        # Sample boundaries (time) for plot view
        min_y_view_limit = max(annotation.start - half_sample_length, 0)
        max_y_view_limit = min(annotation_time_end + half_sample_length, model_total_length)

        min_x_view_limit = max(((3 * annotation.low - annotation.high)/2), - self.model.get_sample_rate()/2)
        max_x_view_limit = min(((3 * annotation.high - annotation.low)/2),  self.model.get_sample_rate()/2)

        self.spectrogram_plot.setRange(yRange=(min_y_view_limit, max_y_view_limit),
                                       xRange=(min_x_view_limit, max_x_view_limit))

        self.roi = AnnotationROI(annotation,
                                 is_selectable=False,
                                 is_time_x_axis=False,
                                 maxBounds=pg.QtCore.QRectF(x,y,w,h),
                                 removable=False)


        self.spectrogram_plot.addItem(self.roi)

        # print(f"Annotation [{annotation.start:.2f}, {annotation.length:.2f}] [{annotation.low:.2f}, {annotation.high:.2f}]\n"
        #       f"Plot limit [{y:.2f}, {y + h:.2f}] [{x:.2f}, {x + w:.2f}]\n"
        #       f"View limit [{min_y_view_limit:.2f}, {max_y_view_limit:.2f}] [{min_x_view_limit:.2f}, {max_x_view_limit:.2f}]\n"
        #       )

        if draw_model_annotations:
            for model_annotation in self.model.annotations:
                if model_annotation != annotation:
                    model_annotation_y = model_annotation.start
                    model_annotation_x = model_annotation.low

                    model_annotation_h = model_annotation.length
                    model_annotation_w = model_annotation.high - model_annotation.low

                    model_annotation_roi = pg.ROI(pos=(model_annotation_x, model_annotation_y),
                                                  size=(model_annotation_w, model_annotation_h),
                                                  movable=False, rotatable=False,
                                                  pen={'color': (100, 100, 100, 200), 'width': 3})

                    self.spectrogram_plot.addItem(model_annotation_roi)

                else:
                    # Do not draw if the annotation is in the model
                    pass

        annotation.annotation_changed.connect(self.update_periodogram)

        self.update_periodogram(annotation)

    def update_periodogram(self, annotation: Annotation):
        annotation_data = self.model.read_time(annotation.start, annotation.length)

        # f, p = signal.periodogram(x=annotation_data,
        #                                 fs=self.model.get_sample_rate(),
        #                                 nfft=1042,
        #                                 window='hann',
        #                                 scaling='spectrum',
        #                                 return_onesided=False)

        f, p = signal.welch(x=annotation_data,
                            fs=self.model.get_sample_rate(),
                            scaling='spectrum',
                            return_onesided=False)

        f = fftpack.fftshift(f)
        p = fftpack.fftshift(p, axes=0)

        self.periodogram_plot.clear()
        self.periodogram_plot.plot(f, p)
