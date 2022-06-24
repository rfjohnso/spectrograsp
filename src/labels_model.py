import logging
import typing

from PySide6 import QtCore, QtWidgets, QtGui


class LabelsModel(QtCore.QAbstractTableModel):

    DEFAULT_COLOR = "#ffffff"
    DEFAULT_LABEL_IDX = 0

    def __init__(self, labels: list = []):
        super(LabelsModel, self).__init__()
        self._labels = labels
        # Colours implemented as look up table
        self.colours = {}

    @property
    def labels(self):
        return self._labels

    def get_label_colour(self, label):
        return self.colours.get(label, self.DEFAULT_COLOR)

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self._labels)

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return 2

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == QtCore.Qt.Orientation.Horizontal:
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                if section == 0:
                    return "Label"
                if section == 1:
                    return "Colour"
        if orientation == QtCore.Qt.Orientation.Vertical:
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                return str(section)

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> typing.Any:        
        if role == QtCore.Qt.ItemDataRole.DisplayRole or role == QtCore.Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                return self._labels[index.row()]
            if index.column() == 1:
                return self.colours.get(self._labels[index.row()], self.DEFAULT_COLOR)
        if role == QtCore.Qt.ItemDataRole.DecorationRole:
            if index.column() == 1:
                label = self._labels[index.row()]
                label_color = self.colours.get(label, self.DEFAULT_COLOR)
                return QtGui.QColor(label_color)
        if role == QtCore.Qt.ItemDataRole.UserRole:
            print("UserRole")
            return self._labels[index.row()]

        return None

    def setData(self, index: QtCore.QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if role == QtCore.Qt.ItemDataRole.EditRole:
            if index.column() == 0:
                self._labels[index.row()] = value
            if index.column() == 1:
                if QtGui.QColor.isValidColor(value):
                    label = self._labels[index.row()]
                    self.colours[label] = value
                    self.dataChanged.emit(index, index)
                else:
                    return False
            return True
        return False

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        index_flags = super(LabelsModel, self).flags(index)
        return index_flags | QtCore.Qt.ItemFlag.ItemIsEditable
        # if index.column() == 1:
        #     return index_flags & ~QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEditable
        # else:
        #     return index_flags | QtCore.Qt.ItemFlag.ItemIsEditable

    def add_label(self, label, colour=None):
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        if not label.strip():
            label = f"default label {self.DEFAULT_LABEL_IDX}"
            self.DEFAULT_LABEL_IDX += 1
        self._labels.append(label)
        self.colours[label] = colour if colour else self.DEFAULT_COLOR
        self.endInsertRows()
        logging.info(f"Added label {label} to label model")

    def remove_labels(self, index):
        self.beginRemoveRows(QtCore.QModelIndex(), index.row(), index.row())
        label = self._labels.pop(index.row())
        logging.info(f"Removed label {label} from label model")
        # We keep the color on the colour lookup table
        # self.colours.pop(label)
        self.endRemoveRows()

    def reset(self):
        self.beginResetModel()
        self._labels = []
        self.endResetModel()





