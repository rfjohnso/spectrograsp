from PySide6 import QtCore, QtWidgets

from groups_model import GroupsModel


class GroupsViewLayout(QtWidgets.QVBoxLayout):

    def __init__(self, parent=None):

        super(GroupsViewLayout, self).__init__(parent)

        self.list_view = QtWidgets.QListView(parent)

        button_layout = QtWidgets.QHBoxLayout()

        self.add_group_button = QtWidgets.QPushButton("Add")
        self.remove_group_button = QtWidgets.QPushButton("Remove")

        button_layout.addWidget(self.add_group_button)
        button_layout.addWidget(self.remove_group_button)

        self.addWidget(self.list_view)
        self.addLayout(button_layout)

        self.add_group_button.clicked.connect(self.add_group)
        self.remove_group_button.clicked.connect(self.remove_group)

    def set_model(self, model: GroupsModel):
        self.list_view.setModel(model)
        self.list_view.selectionModel().selectionChanged.connect(self.group_selection_changed)

    @QtCore.Slot()
    def add_group(self):
        if self.list_view.model():
            self.list_view.model().add_group("")

    @QtCore.Slot()
    def remove_group(self):
        if self.list_view.model():
            self.list_view.model().remove_group(
                self.list_view.selectionModel().currentIndex())

    @QtCore.Slot()
    def group_selection_changed(self, selected, deselected):
        self.remove_group_button.setEnabled(selected.count() > 0)
