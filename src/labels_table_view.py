from labels_model import LabelsModel

from PySide6 import QtCore, QtWidgets


class ColorSelectionDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        super(ColorSelectionDelegate, self).__init__(parent)

    def createEditor(self, parent: QtWidgets.QWidget, option: 'QStyleOptionViewItem',
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        color_picker = QtWidgets.QColorDialog(parent)
        return color_picker

    def setEditorData(self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex) -> None:
        pass

    def setModelData(self, editor: QtWidgets.QColorDialog, model: QtCore.QAbstractItemModel,
                     index: QtCore.QModelIndex) -> None:
        if editor.result() == QtWidgets.QDialog.Accepted:
            model.setData(index, editor.currentColor().name(), QtCore.Qt.ItemDataRole.EditRole)


class LabelsViewLayout(QtWidgets.QVBoxLayout):

    def __init__(self, parent=None):
        super(LabelsViewLayout, self).__init__(parent)

        self.table_view = QtWidgets.QTableView(parent)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.setItemDelegateForColumn(1, ColorSelectionDelegate(self.table_view))
        self.table_view.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table_view.setSelectionMode(QtWidgets.QTableView.SingleSelection)

        button_layout = QtWidgets.QHBoxLayout()

        self.add_label_button = QtWidgets.QPushButton("Add")
        self.remove_label_button = QtWidgets.QPushButton("Remove")

        self.remove_label_button.setDisabled(True)

        button_layout.addWidget(self.add_label_button)
        button_layout.addWidget(self.remove_label_button)

        self.addWidget(self.table_view)
        self.addLayout(button_layout)

        self.add_label_button.clicked.connect(self.add_label)
        self.remove_label_button.clicked.connect(self.remove_label)

    def set_model(self, model: LabelsModel):
        self.table_view.setModel(model)
        self.table_view.selectionModel().selectionChanged.connect(self.label_selection_changed)

    @QtCore.Slot()
    def add_label(self):
        if self.table_view.model():
            self.table_view.model().add_label("")

    @QtCore.Slot()
    def remove_label(self):
        if self.table_view.model():
            self.table_view.model().remove_labels(
                self.table_view.selectionModel().currentIndex())

    @QtCore.Slot()
    def label_selection_changed(self, selected, deselected):
        self.remove_label_button.setEnabled(selected.count() > 0)
