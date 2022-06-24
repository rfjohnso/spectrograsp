import logging
from typing import Union, Any
from PySide6 import QtWidgets, QtCore
from ui.ui_onnx_inference_dialog import Ui_onnx_inference_dialog
from pathlib import Path
import onnx
from onnxruntime import InferenceSession


class LabelsModel(QtCore.QAbstractTableModel):
    
    def __init__(self, labels: list = []):
        super(LabelsModel, self).__init__()
        self.labels = labels
        self.setHeaderData(0, QtCore.Qt.Horizontal, "Labels", QtCore.Qt.ItemDataRole.DisplayRole)

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self.labels)

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return 1

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...) -> Any:
        if orientation == QtCore.Qt.Orientation.Horizontal:
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                if section == 0:
                    return "Labels"
        if orientation == QtCore.Qt.Orientation.Vertical:
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                return str(section)

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        if not index.isValid():
            return None
        if role == QtCore.Qt.ItemDataRole.DisplayRole or role == QtCore.Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                return self.labels[index.row()]
            else:
                return None
        return None

    def setData(self, index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex], value: Any, role: int= ...) -> bool:
        if role == QtCore.Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                self.labels[index.row()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        index_flags = super(LabelsModel, self).flags(index)
        return index_flags | QtCore.Qt.ItemFlag.ItemIsEditable

    def add_label(self, label):
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        self.labels.append(label)
        self.endInsertRows()

    def clear(self):
        self.beginResetModel()
        self.labels = []
        self.endResetModel()


class ONNXModelDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(ONNXModelDialog, self).__init__(parent)

        self.ui = Ui_onnx_inference_dialog()
        self.ui.setupUi(self)

        self.sess = None
        self.output_index = 0

        self.labels_model = LabelsModel()
        self.ui.labels_tableview.setModel(self.labels_model)

        self.ui.open_model_button.clicked.connect(self.open_onnx_model)
        self.ui.open_labels_button.clicked.connect(self.open_labels)

        self.settings = QtCore.QSettings("config.ini", QtCore.QSettings.IniFormat)

    def open_onnx_model(self):

        default_onnx_dir = self.settings.value("dir/last_onnx_inference_dir")

        model_file, extension = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                      "Open ONNX model",
                                                                      default_onnx_dir,
                                                                      "ONNX model (*.onnx)")
        if model_file:

            self.settings.setValue("dir/last_onnx_inference_dir", model_file)

            try:
                self.sess = InferenceSession(model_file, providers=['CPUExecutionProvider'])
            except Exception as error:
                raise error
            else:

                if len(self.sess.get_inputs()) != 1:
                    logging.warning(f"Multiple input not supported")
                    QtWidgets.QMessageBox.warning(self, "Invalid input", "Multiple input is not supported")
                    return

                model_input = self.sess.get_inputs()[0]

                if len(self.sess.get_outputs()) != 1:
                    logging.warning(f"Multiple output not supported")
                    QtWidgets.QMessageBox.warning(self, "Invalid output", "Multiple output is not supported")
                    return

                model_output = self.sess.get_outputs()[self.output_index]

                if len(model_output.shape) > 2:
                    logging.warning(f"Output shape not supported")
                    QtWidgets.QMessageBox.warning(self, "Invalid output shape", f"Output shape {model_output.shape} is not supported")
                    return

                model_metadata = self.sess.get_modelmeta()

                self.ui.model_file_value.setText(Path(model_file).name)

                self.ui.model_name_value.setText(model_metadata.graph_name)
                self.ui.model_version_value.setText(f"{model_metadata.version}")

                # Model input
                self.ui.model_input_value.setText(f"{model_input.name}")
                self.ui.model_input_shape_value.setText(f"{', '.join(map(str, model_input.shape))}")
                self.ui.model_input_type_value.setText(f"{model_input.type}")
                # Model output
                self.ui.model_output_value.setText(f"{model_output.name} ")
                self.ui.model_output_shape_value.setText(f"{', '.join(map(str, model_output.shape))}")
                self.ui.model_output_type_value.setText(f"{model_output.type}")

                self.labels_model.clear()
                for n in range(model_output.shape[-1]):
                    self.labels_model.add_label(f"Default label {n}")

                # TODO: let user select which model output to use
                # self.ui.model_output_values.clear()
                # self.ui.model_output_values.addItems([output.name for output in self.sess.get_outputs()])
                # self.ui.model_output_values.currentIndexChanged.connect(self.set_model_output)
                # self.ui.model_output_values.setCurrentIndex(0)

                self.ui.model_producer_value.setText(f"{model_metadata.producer_name}")
                self.ui.model_domain_value.setText(f"{model_metadata.domain}")

                # We need a way to store the model version and I do not think model versioning is the right tool
                # https://github.com/onnx/onnx/blob/master/docs/Versioning.md#model-versioning
        else:
            pass

    def set_model_output(self, output_index):
        print(output_index)
        model_output = self.sess.get_outputs()[output_index]
        if len(model_output.shape > 2):
            logging.warning(f"Output shape not supported")
            QtWidgets.QMessageBox.warning(self, "Invalid input", "Multiple input is not supported")

            self.ui.model_output_shape_value.setText(f"{','.join(map(str, model_output.shape))}")

            self.output_index = output_index

    def open_labels(self):

        default_onnx_dir = self.settings.value("dir/last_onnx_inference_dir")

        label_file, extension = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                      "Open labels file",
                                                                      default_onnx_dir,
                                                                      "Text file (*.txt, *)")
        if label_file:
            with open(label_file, 'r') as label_file:
                # Read each line a different label removing empty lines and empty characters
                labels = [line.strip() for line in label_file if line.strip()]
                if self.sess:
                    # Check output shape (las dim by default) and labels length
                    output_shape = self.sess.get_outputs()[self.output_index].shape
                    if output_shape[-1] != len(labels):

                        QtWidgets.QMessageBox.warning(self,
                                                      "ONNX labels errors",
                                                      f"Number of labels in file {len(labels)} "
                                                      f"does not match with model output shape {output_shape[-1]}")
                        return
                self.labels_model.clear()
                map(self.labels_model.add_label, labels)
