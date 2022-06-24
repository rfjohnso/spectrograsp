import logging
from typing import Union, Any
from PySide6 import QtCore, QtWidgets, QtGui


class GroupsModel(QtCore.QAbstractListModel):

    DEFAULT_GROUP_IDX = 0

    def __init__(self, groups: list = []):
        super(GroupsModel, self).__init__()
        self._groups = groups

    @property
    def groups(self):
        return self._groups

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self._groups)

    def data(self, index: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex], role:int=...) -> Any:
        if role == QtCore.Qt.ItemDataRole.DisplayRole or role == QtCore.Qt.ItemDataRole.EditRole:
            return self._groups[index.row()]

    def setData(self, index:Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex], value:Any, role:int=...) -> bool:
        if role == QtCore.Qt.ItemDataRole.EditRole:
            self._groups[index.row()] = value
            return True
        return False

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        index_flags = super(GroupsModel, self).flags(index)
        return index_flags | QtCore.Qt.ItemFlag.ItemIsEditable

    def add_group(self, group):
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        if not group.strip():
            group = f"Default group {self.DEFAULT_GROUP_IDX}"
            self.DEFAULT_GROUP_IDX += 1
        self._groups.append(group)
        self.endInsertRows()
        logging.info(f"Added group {group} to group model")

    def remove_group(self, index):
        self.beginRemoveRows(QtCore.QModelIndex(), index.row(), index.row())
        group = self.data(index, QtCore.Qt.ItemDataRole.DisplayRole)
        self._groups.remove(group)
        # We keep the color on the colour lookup table
        # self.colours.pop(label)
        self.endRemoveRows()
        logging.info(f"Removed group {group} from group model")

    def reset(self):
        self.beginResetModel()
        self._groups = []
        self.endResetModel()

