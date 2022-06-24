import logging
import sys

from PySide6 import QtCore, QtWidgets, QtGui

from spectrogram_view import SpectrogramView
from annotations_tree_view import AnnotationTreeView
from automatic_annotation import AutomaticAnnotation
from onnx_inference import ONNXInference
from digital_rf_dialog import DigitalRFDialog
from sigmf_dialog import SigMFDialog

from sigmf_model import SigMFModel
from digitalrf_model import DigitalRFModel

from ui.ui_about_dialog import Ui_AboutDialog

WINDOW_TITLE = 'SpectroGrasp'

class SpectroGraspMainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = None
        self.setupUI()
        self.settings = QtCore.QSettings("config.ini", QtCore.QSettings.IniFormat)

    def setupUI(self):

        self.setWindowTitle(WINDOW_TITLE)
        self.setMenuBar(self._menu_bar())

        self.setStatusBar(QtWidgets.QStatusBar(self))

        main_widget = QtWidgets.QWidget(self)
        main_layout = QtWidgets.QHBoxLayout(main_widget)

        self.plot = SpectrogramView()

        self.annotations_view = AnnotationTreeView()
        self.annotations_view.hide()

        # self.annotation_dock = QtWidgets.QDockWidget(self)
        #
        # self.annotation_dock.setWidget(self.annotations_view)
        # self.annotation_dock.setWindowTitle("Annotation")
        #
        # self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.annotation_dock)

        # Changed widget to dockdwidget
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, main_widget)
        splitter.addWidget(self.plot)
        splitter.addWidget(self.annotations_view)

        self.left_panel = QtWidgets.QWidget(self)
        self.left_panel.setLayout(QtWidgets.QVBoxLayout())
        self.left_panel.setMaximumWidth(300)

        self.left_panel.hide()

        # self.sigmf_metadata_view = SigMFMetadataView(self.left_panel)
        # self.digitalrf_metadata_view = DigitalRFMetadataView(self.left_panel)
        #
        # left_panel_layout.addWidget(self.sigmf_metadata_view)
        # left_panel_layout.addWidget(self.digitalrf_metadata_view)
        # left_panel_layout.addWidget(self.plot.get_spectrogram_parameter_view())
        #
        # self.left_panel.setLayout(left_panel_layout)

        self.left_panel.layout().addWidget(self.plot.get_spectrogram_parameter_view())

        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(splitter)

        self.setCentralWidget(main_widget)

    def _menu_bar(self):
        menu = QtWidgets.QMenuBar(self)

        # Menu files
        menu_files = menu.addMenu("Files")
        # Menu open
        open_menu = menu_files.addMenu("Open")
        # Action open sigmf
        action_open_sigmf = QtGui.QAction(text="Open SigFM", parent=self)
        action_open_sigmf.triggered.connect(self._open_sigmf)
        # Action open digitalrf
        action_open_digitalrf = QtGui.QAction(text="Open DigitalRF", parent=self)
        action_open_digitalrf.triggered.connect(self._open_digitalrf)

        open_menu.addActions([action_open_sigmf, action_open_digitalrf])

        # Action save file
        action_save = QtGui.QAction(text="Save", parent=self)
        action_save.triggered.connect(self._save)
        # Action save file as
        action_save_as = QtGui.QAction(text="Save as", parent=self)
        action_save_as.triggered.connect(self._save_as)

        menu_files.addActions([action_save, action_save_as])
        menu_files.addSeparator()

        # Action quit app
        action_quit = QtGui.QAction(text="Quit", parent=self)
        action_quit.triggered.connect(self.close)

        menu_files.addActions([action_quit])

        # Menu Analysis
        menu_analysis = menu.addMenu("Analysis")
        # Action automatic annotation
        action_automatic_annotation = QtGui.QAction(text="Automatic annotation", parent=self)
        action_automatic_annotation.triggered.connect(self._automatic_annotation)
        # Action automatic symbol rate
        action_symbol_rate = QtGui.QAction(text="Symbol rate", parent=self)
        action_symbol_rate.setCheckable(True)
        action_symbol_rate.triggered.connect(self._symbol_rate_triggered)
        # action_symbol_rate.toggled.connect(self._symbol_rate_toggled)

        menu_analysis.addActions([action_automatic_annotation, action_symbol_rate])

        menu_analysis.addSeparator()

        # Action automatic symbol rate
        action_onnx_runtime = QtGui.QAction(text="ONNX Runtime", parent=self)
        action_onnx_runtime.triggered.connect(self._onnx_runtime)

        menu_analysis.addActions([action_onnx_runtime])

        # Menu help
        menu_about = menu.addMenu("Help")
        # Action about
        action_about = QtGui.QAction(text="About", parent=self)
        action_about.triggered.connect(self._about)

        menu_about.addActions([action_about])

        return menu


    @QtCore.Slot()
    def _open_sigmf(self):

        file = QtWidgets.QFileDialog.getOpenFileName(
            dir=self.settings.value('dir/last_sigmf_dir'),
            caption="Select SigMF files",
            filter="SigMF (*.sigmf)")

        if file[0]:
            logging.debug(f"Opening sigmf file {file[0]}")

            try:
                self.model = SigMFModel(file[0])
            except Exception as error:
                QtWidgets.QMessageBox.critical(self, "SigMF error", str(error))
                print(error)
            else:
                self.model_dialog = SigMFDialog(self)
                self.model_dialog.set_model(self.model)

                self.model_dialog.exec()

                if self.model_dialog.result() == QtWidgets.QDialog.Accepted:
                    # Update GUI with file metadata
                    self.setWindowTitle(f"{WINDOW_TITLE} - {file[0]}")
                    self.statusBar().showMessage(
                        f"Samples: {self.model.get_sample_count()} | Annotations: {len(self.model.annotations)}")

                    self.plot.set_model(self.model)
                    self.annotations_view.set_model(self.model)

                    self.annotations_view.show()
                    self.left_panel.show()

                else:
                    pass

            self.settings.setValue("dir/last_sigmf_dir", file[0])
        else:
            logging.debug("No file selected opening SigMF")


    @QtCore.Slot()
    def _open_digitalrf(self):

        default_dir = self.settings.value('dir/last_digitalrf_dir')

        # folder = QtWidgets.QFileDialog.get(dir=default_dir)
        file = QtWidgets.QFileDialog.getOpenFileName(
            dir=self.settings.value('dir/last_digitalrf_dir'),
            caption="Select Digital RF channel",
            filter="Digital RF channel (drf_properties.h5)")

        if not file[0]:
            logging.debug("No file selected opening DigitalRF")
            return
        else:
            self.settings.setValue("dir/last_digitalrf_dir", file[0])

        try:
            self.model = DigitalRFModel(file[0])
        except ValueError as value_error:
            QtWidgets.QMessageBox.critical(self, "DigitaRF error", str(value_error))
            print(value_error)
        except Exception as error:
            QtWidgets.QMessageBox.warning(self, "DigitaRF error", str(error))
            print(error)
        else:

            self.model_dialog = DigitalRFDialog(self)
            self.model_dialog.set_model(self.model)
            self.model_dialog.exec()

            if self.model_dialog.result() == QtWidgets.QDialog.Accepted:
                self.setWindowTitle(f"{WINDOW_TITLE} - {self.model.get_channel()}")

                self.statusBar().showMessage(
                    f"Samples: {self.model.get_sample_count()} | Annotations: {len(self.model.annotations)}")

                self.plot.set_model(self.model)
                self.annotations_view.set_model(self.model)
                # self.digitalrf_metadata_view.set_model(self.model)
                #
                # self.sigmf_metadata_view.hide()
                # self.digitalrf_metadata_view.show()

                self.annotations_view.show()
                self.left_panel.show()
            else:
                pass


    @QtCore.Slot()
    def _save(self):
        if self.model:
            try:
                self.model.save()
            except Exception as error:
                result = QtWidgets.QMessageBox.critical(self, "Error saving", str(error))
            else:
                self.model.modified_status = False


    @QtCore.Slot()
    def _save_as(self):
        if self.model:
            if isinstance(self.model, SigMFModel):
                file = QtWidgets.QFileDialog.getSaveFileName(
                    dir=self.model.file_name,
                    caption="Select SigMF files",
                    filter="SigMF (*.sigmf)")
                destination = file[0]

            if isinstance(self.model, DigitalRFModel):
                folder = QtWidgets.QFileDialog.getExistingDirectory(
                    dir=str(self.model.channel_path),
                    caption="Select DigitalRF metadata folder")
                destination = folder

            if destination:
                try:
                    self.model.save(destination)
                except Exception as error:
                    result = QtWidgets.QMessageBox.critical(self, "Error saving", str(error))
                else:
                    self.model.modified_status = False
            else:
                # No destination
                pass
        else:
            # No model
            pass

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.settings.setValue("geometry", self.saveGeometry())
        #TODO: Check status before closing
        if self.model and self.model._modified:
            reply = QtWidgets.QMessageBox.question(self, "File modified", "Would you like to close without saving?")
            if reply == QtWidgets.QMessageBox.Yes:
                logging.info("Saving before closing")
                # self._save()
                event.accept()
            elif reply == QtWidgets.QMessageBox.No:
                logging.info("Closing canceled because model was modified")
                event.ignore()
        else:
            event.accept()

    @QtCore.Slot()
    def _automatic_annotation(self):
        if self.model:
            aa = AutomaticAnnotation(parent=self, model=self.model)
            # Show the automatic annotation configuration dialog
            aa_configuration_result = aa.configure_automatic_annotation()
            if aa_configuration_result == QtWidgets.QDialog.Accepted:
                # This will show the automatic annotation modal dialog
                aa.start_automatic_annotation()

    @QtCore.Slot(bool)
    def _symbol_rate_triggered(self, checked):
        print("Symbol rate triggered", checked)
        pass

    @QtCore.Slot(bool)
    def _symbol_rate_toggled(self, checked):
        print("Symbol rate toggled", checked)
        pass

    @QtCore.Slot()
    def _onnx_runtime(self):
        if self.model:
            onnx_runtime = ONNXInference(parent=self, model=self.model)
            onnx_config_result = onnx_runtime.configure_onnx_inference()
            if onnx_config_result == QtWidgets.QDialog.Accepted:
                onnx_runtime.start_onnx_inference()


    @QtCore.Slot()
    def _about(self):
        about_dialog = QtWidgets.QDialog(self)
        ui_about_dialog = Ui_AboutDialog()
        ui_about_dialog.setupUi(about_dialog)
        about_dialog.show()    


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    app = QtWidgets.QApplication([])
    app.setOrganizationName("REDS")
    app.setApplicationName("SpectroGrasp")

    main = SpectroGraspMainWindow()
    main.restoreGeometry(main.settings.value("geometry"))

    main.show()

    try:
        return_code = app.exec()
    except Exception as error:
        print(error)
        print(logging)
        sys.exit(-1)
    else:
        sys.exit(return_code)

