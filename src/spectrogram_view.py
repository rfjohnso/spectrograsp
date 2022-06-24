import logging

from PySide6 import QtCore, QtWidgets, QtGui

import numpy as np
import pyqtgraph as pg

from scipy import signal, fftpack

from annotation import Annotation, AnnotationSource
from annotation_roi import AnnotationROI
from sigmf_model import SigMFModel
from spectrogram_parameters_view import SpectrogramParametersView
from annotation_dialog import AnnotationDialog

# pg.setConfigOptions(imageAxisOrder='row-major')
pg.setConfigOptions(antialias=True)
# pg.setConfigOptions(useOpenGL=True)

colors = [(38, 70, 83), (42, 157, 143), (233, 196, 106), (244, 162, 97), (231, 111, 81)]


class SpectrogramViewBox(pg.ViewBox):

    def __init__(self, **kwargs):
        super(SpectrogramViewBox, self).__init__(**kwargs)

        self.menu = QtWidgets.QMenu()
        self.remove_selected = QtGui.QAction("Remove selected ROI", self.menu)
        self.merge_selected = QtGui.QAction("Merge selected ROI", self.menu)
        self.group_selected = QtGui.QAction("Group selected ROI", self.menu)

        self.menu.addActions([self.remove_selected, self.merge_selected, self.group_selected])

    def getMenu(self, ev):
        return self.menu


class SpectrogramView(pg.PlotWidget):

    def __init__(self, parent=None):

        self.view_box = SpectrogramViewBox()

        # Connect view box events
        self.view_box.merge_selected.triggered.connect(self.merge_selected_annotations)
        self.view_box.remove_selected.triggered.connect(self.remove_selected_annotations)
        self.view_box.group_selected.triggered.connect(self.group_selected_annotations)
        self.view_box.sigRangeChangedManually.connect(self.sigRegionChanged)
        # self.view_box.sigXRangeChanged.connect(self.test)

        super(SpectrogramView, self).__init__(parent=parent, viewBox=self.view_box)

        colormap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 5), color=colors)
        # colormap = pg.colormap.get('turbo_r', source='matplotlib', skipCache=True)
        # self.image = pg.ImageItem(lut=colormap.getLookupTable())
        self.image = pg.ImageItem()
        self.image.setOpts(axisOrder='row-major')

        self.colorbar = pg.ColorBarItem(interactive=True, cmap=colormap, label="Power")
        self.colorbar.setImageItem(self.image, insert_in=self.getPlotItem())
        self.colorbar.hide()

        # self.pos_label = self.add

        # self.histogram = pg.HistogramLUTItem(self.image)
        # self.addItem(self.histogram)

        self.annotation_dialog = AnnotationDialog(self)

        # Setup axes
        self.getPlotItem().setLabel('bottom', 'Time', units='s')
        self.getPlotItem().setLabel('left', 'Frequency', units='Hz')

        # self.getPlotItem().showGrid(alpha=0.5)
        self.getPlotItem().setMenuEnabled(enableMenu=False, enableViewBoxMenu=True)

        self.getPlotItem().layout.setContentsMargins(10, 25, 25, 10)

        self.getPlotItem().setMouseEnabled(y=True, x=True)

        self.edit_mode = False
        self.edit_new_roi = False

        settings = QtCore.QSettings("config.ini", QtCore.QSettings.IniFormat)

        settings.beginGroup('spectrogram')

        self.set_spectrogram_params(settings.value('nperseg'),
                                    settings.value('window'),
                                    settings.value('noverlap'),
                                    settings.value('nttf'))

    def remove_selected_annotations(self):
        selected_annotations = self.model.get_selected_annotations()
        if len(selected_annotations) > 1:
            msg = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Question,
                "Deleted selected annotations",
                f"Are you sure you want to delete {len(selected_annotations)} annotations?")
            msg.addButton(QtWidgets.QMessageBox.Yes)
            msg.addButton(QtWidgets.QMessageBox.No)
            msg.setDefaultButton(QtWidgets.QMessageBox.No)

            delete_confirmation = msg.exec()

            if delete_confirmation == QtWidgets.QMessageBox.Yes:
                self.model.remove_selected_annotations()

    def merge_selected_annotations(self):

        selected_annotations = self.model.get_selected_annotations()
        if len(selected_annotations) > 1:
            msg = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Question,
                "Merge selected annotations",
                f"Are you sure you want to merge {len(selected_annotations)} annotations?")
            msg.addButton(QtWidgets.QMessageBox.Yes)
            msg.addButton(QtWidgets.QMessageBox.No)
            msg.setDefaultButton(QtWidgets.QMessageBox.No)

            delete_confirmation = msg.exec()

            if delete_confirmation == QtWidgets.QMessageBox.Yes:
                self.model.merge_selected_annotations()

    def group_selected_annotations(self):

        group_dialog = QtWidgets.QDialog(self)

        group_dialog.setWindowTitle("Annotation group")

        group_dialog_layout = QtWidgets.QVBoxLayout()

        group_dialog_combobox = QtWidgets.QComboBox()
        group_dialog_combobox.setModel(self.model.groups)
        group_dialog_combobox.setEditable(True)
        # group_dialog_combobox.setCompleter(QtWidgets.QCompleter(model=self.model.groups, parent=group_dialog))
        group_dialog_combobox.setCurrentIndex(-1)

        group_dialog_button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                                             QtWidgets.QDialogButtonBox.Cancel)

        group_dialog_button_box.accepted.connect(group_dialog.accept)
        group_dialog_button_box.rejected.connect(group_dialog.reject)

        group_dialog_layout.addWidget(QtWidgets.QLabel("Select or introduce new group:"))
        group_dialog_layout.addWidget(group_dialog_combobox)
        group_dialog_layout.addWidget(group_dialog_button_box)

        group_dialog.setLayout(group_dialog_layout)

        if group_dialog.exec() == QtWidgets.QDialog.Accepted:
            group_value = group_dialog_combobox.currentText()
            if not group_value:
                QtWidgets.QMessageBox.warning(group_dialog,
                                              "Invalid group",
                                              f"You must introduce a valid group ({group_value})")
            else:
                for annotation in self.model.get_selected_annotations():
                    annotation.group = group_value
                    annotation.annotation_changed.emit(annotation)
                self.model.groups.add_group(group_value)
        else:
            pass

    def export_annotation(self, annotation):
        #TODO: add support for different formats
        # file_formats = ["Binary", "Numpy (*.npy)", "Matlab (*.mat)", "CSV (*.csv)"]
        export_file, export_extension = QtWidgets.QFileDialog.getSaveFileName(self, 'Open file', '.')
        if export_file:
            self.model.export_annotations(annotation, export_file)

    @QtCore.Slot()
    def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
        if ev.matches(QtGui.QKeySequence.Delete):
            self.model.remove_selected_annotations()

        if ev.key() == QtCore.Qt.Key.Key_Control:
            self.edit_mode = True
            self.setCursor(QtCore.Qt.CursorShape.CrossCursor)

        self.scene().keyPressEvent(ev)

    @QtCore.Slot()
    def keyReleaseEvent(self, ev: QtGui.QKeyEvent) -> None:
        if ev.key() == QtCore.Qt.Key.Key_Control:
            self.edit_mode = False
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

        self.scene().keyReleaseEvent(ev)


    def set_model(self, model: SigMFModel):

        self.model = model

        # Get model last sample time mark
        model_time_limit = self.model.sample_to_time(self.model.get_sample_count())
        # Assume symmetry around central frequency
        model_freq_limit = self.model.get_central_frequency() + self.model.get_sample_rate()//2

        # Update plot limits
        self.getPlotItem().setLimits(xMin=0, xMax=model_time_limit,
                                     yMin=-model_freq_limit, yMax=model_freq_limit)
        # Read all data
        self.data = model.read_samples()

        # Clean the plotItem (this includes all images)
        self.getPlotItem().clear()
        # Add the main image
        self.addItem(self.image, row=0, col=0)

        # Update plot with read data from model
        self.update()

        # Add annotations from the model to the plot
        for annotation in self.model.annotations:
            self.add_annotation(annotation)

        self.annotation_dialog.set_model(model)

        # Link model annotations events with view
        self.model.annotation_added.connect(self.add_annotation)
        self.model.annotation_removed.connect(self.remove_annotation)

    def set_spectrogram_params(self, nperseg=None, window=None, noverlap=None, nfft=None):
        #TODO: Add parameters checkings
        self.nperseg = nperseg
        self.window  = window
        self.noverlap = noverlap
        self.nfft = nfft

    def update(self):
        # Compute spectrogram
        f, t, sxx = signal.spectrogram(self.data,
                                       fs=self.model.get_sample_rate(),
                                       nperseg=self.nperseg,
                                       # window=self.window,
                                       noverlap=self.noverlap,
                                       nfft=self.nfft,
                                       return_onesided=False)

        # Frequency shift for both sides
        f = fftpack.fftshift(f)
        sxx = fftpack.fftshift(sxx, axes=0)

        # Spectrogram log scale
        sxx_log = 10 * np.log10(sxx)

        x = 0 * self.model.get_sample_rate()
        w = self.data.shape[0] / self.model.get_sample_rate()

        y = 0 - self.model.get_sample_rate()/2
        h = self.model.get_sample_rate()

        self.image.setImage(sxx_log, rect=[x, y, w, h])

        self.colorbar.lo_lim = np.min(sxx_log)
        self.colorbar.hi_lim = np.max(sxx_log)

        self.colorbar.setLevels(low=np.min(sxx_log), high=np.max(sxx_log))

        self.colorbar.show()


    @QtCore.Slot(object)
    def add_annotation(self, annotation: Annotation):
        # View box limits defines the max/min x,y values of the whole plot (ref set_model)
        vb_limits = self.getPlotItem().getViewBox().getState()['limits']

        annotation_roi = AnnotationROI(annotation,
                                       maxBounds=pg.QtCore.QRectF(
                                           vb_limits['xLimits'][0],
                                           vb_limits['yLimits'][0],
                                           vb_limits['xLimits'][1] - vb_limits['xLimits'][0],
                                           vb_limits['yLimits'][1] - vb_limits['yLimits'][0])
                                       )

        # annotation_roi.maxBounds = self.getPlotItem().vb.boundingRect()
        annotation_roi.sigRemoveRequested.connect(self.remove_roi)
        annotation_roi.export_roi_signal.connect(self.export_annotation)
        annotation_roi.open_roi_signal.connect(self.open_roi)
        annotation_roi.setPen(self.model.labels.get_label_colour(annotation.label))

        self.addItem(annotation_roi)

    @QtCore.Slot(object)
    def remove_roi(self, roi):
        logging.debug(f"Remove ROI at {roi.pos()}")
        # self.removeItem(roi)
        self.model.remove_annotation(roi.annotation)

    @QtCore.Slot(object)
    def open_roi(self, annotation):
        self.annotation_dialog.set_annotation(annotation)
        self.annotation_dialog.exec()

    @QtCore.Slot(object)
    def remove_annotation(self, annotation: Annotation):
        logging.debug(f"Remove annotation at {annotation.start}")
        for item in self.getPlotItem().items:
            if isinstance(item, AnnotationROI) and item.annotation == annotation:
                self.removeItem(item)
                break

    def mousePressEvent(self, ev):
        """ Capture mouse press event to start drawing ROI
        :param ev
        """
        if self.edit_mode and not self.edit_new_roi and ev.button() == QtCore.Qt.LeftButton:

            new_roi_pos = self.plotItem.vb.mapSceneToView(ev.pos())

            self.new_roi = pg.ROI(new_roi_pos,
                                  size=[0, 0],
                                  pen=pg.mkPen(color='w', width=2),
                                  snapSize=0.1,
                                  rotatable=False,
                                  removable=True)

            self.addItem(self.new_roi)

            self.edit_new_roi = True

            logging.debug(f"Start drawing new ROI at {new_roi_pos}")
        else:
            super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev):
        """ Capture mouse release event to end drawing the new ROI and create and annotation
        :param ev: Mouse release event
        """
        if self.edit_mode and ev.button() == QtCore.Qt.LeftButton:

            new_roi_pos = self.new_roi.pos()
            new_roi_size = self.new_roi.size()

            if not new_roi_size.isNull():

                logging.debug(f"Ended drawing new ROI starting at {new_roi_pos} with size {new_roi_size}")

                if new_roi_size[0] < 0:
                    # Negative size means
                    start = new_roi_pos[0] + new_roi_size[0]
                    duration = - new_roi_size[0]
                else:
                    start = new_roi_pos[0]
                    duration = new_roi_size[0]

                freq_1 = new_roi_pos[1]
                freq_2 = new_roi_pos[1] + new_roi_size[1]

                high = max(freq_1, freq_2)
                low  = min(freq_1, freq_2)

                # Create annotation from drawn ROI
                new_annotation = Annotation(source=AnnotationSource.USER,
                                            start=start, length=duration,
                                            high=high, low=low)

                # Add annotation to the model
                self.model.add_annotation(new_annotation)

            else:
                logging.warning("New ROI has null size and won't be added")

            # New ROI edition ended
            self.edit_new_roi = False
            # Remove drawn form plot
            self.plotItem.removeItem(self.new_roi)
        else:
            super().mouseReleaseEvent(ev)

    def mouseMoveEvent(self, ev):
        """ Capture mose event and change drawing ROI size
        """
        if self.edit_mode and self.edit_new_roi:
            new_roi_pos = self.plotItem.vb.mapSceneToView(ev.pos())
            self.new_roi.setSize(new_roi_pos - self.new_roi.pos())
        else:
            super().mouseMoveEvent(ev)

    @QtCore.Slot()
    def sigRegionChanged(self, ev):
        print(ev)
        if ev[0]:
            x_view_range = self.view_box.viewRange()[0]
            print("X axis range", x_view_range)
            # self.data = self.model.read_time(x_view_range[0], x_view_range[1] - x_view_range[0])
            # print(self.data.shape, self.data.nbytes/1024**2)
        else:
            print("X axis did not change")

    @QtCore.Slot()
    def test(self):
        print("test", self.getPlotItem().getViewBox().viewRect())
        pass

    def get_spectrogram_parameter_view(self):

        view = SpectrogramParametersView(nperseg=self.nperseg,
                                         window=self.window,
                                         noverlap=self.noverlap,
                                         nfft=self.nfft)

        view.update_signal.connect(self.update_scene)
        return view

    @QtCore.Slot(int, str, int, int)
    def update_scene(self, nperseg, window, noverlap, nfft):

        logging.debug(f"Update scene ({self.nperseg}, {self.window}, {self.noverlap}, {self.nfft}")

        # self.nperseg = None if nperseg == 0 else nperseg
        self.nperseg = nperseg or None
        self.noverlap = None if noverlap == 0 else noverlap
        self.nfft = None if nfft == 0 else nfft

        self.update()
