import logging

from PySide6 import QtCore, QtWidgets, QtGui

from annotation import Annotation
from sigmf_model import SigMFModel

logging = logging.getLogger("SpectroGrasp")


class AnnotationTreeItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, annotation: Annotation):
        super(AnnotationTreeItem, self).__init__()

        self.annotation = annotation
        self.setupUI()

    def setupUI(self):

        self.setText(0, "Annotation")
        self.setSizeHint(0, QtCore.QSize(0, 20))
        # Annotation item flags:
        # - Selectable (annotation select)
        # - Drag enabled (annotation drag/drop group)
        # - Drop disabled (annotation cannot be destination of a drop)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)

        self.start_item = self.create_annotation_field_item("Start")
        self.duration_item = self.create_annotation_field_item("Duration")
        self.low_freq_item = self.create_annotation_field_item("Low freq.")
        self.high_freq_item = self.create_annotation_field_item("High freq.")
        self.author_item = self.create_annotation_field_item("Author")
        self.comment_item = self.create_annotation_field_item("Comment")
        self.label_item = self.create_annotation_field_item("Label")

        self.update_annotation_data()

    def create_annotation_field_item(self, label):
        item = QtWidgets.QTreeWidgetItem(self)
        item.setData(0, QtCore.Qt.ItemDataRole.DisplayRole, label)
        item.setSizeHint(0, QtCore.QSize(0, 20))
        # Annotation field item flags: Not selectable, drag disabled, drop disabled
        item.setFlags(item.flags() &
                      ~QtCore.Qt.ItemIsSelectable &
                      ~QtCore.Qt.ItemIsDragEnabled &
                      ~QtCore.Qt.ItemIsDropEnabled)
        return item

    def update_annotation_data(self):
        self.start_item.setData(1, QtCore.Qt.ItemDataRole.DisplayRole, f"{self.annotation.start:.02f}")
        self.duration_item.setData(1, QtCore.Qt.ItemDataRole.DisplayRole, f"{self.annotation.length:.02f}")
        self.low_freq_item.setData(1, QtCore.Qt.ItemDataRole.DisplayRole, f"{self.annotation.low:.02f}")
        self.high_freq_item.setData(1, QtCore.Qt.ItemDataRole.DisplayRole, f"{self.annotation.high:.02f}")
        self.author_item.setData(1, QtCore.Qt.ItemDataRole.DisplayRole, self.annotation.author)
        self.comment_item.setData(1, QtCore.Qt.ItemDataRole.DisplayRole, self.annotation.comment)


class AnnotationTreeView(QtWidgets.QTreeWidget):
    
    def __init__(self, parent=None):
        super(AnnotationTreeView, self).__init__(parent)

        self.setColumnCount(1)
        self.setHeaderLabels(["Groups", "Values"])
        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setColumnWidth(0, 125)

        # self.setDragEnabled(False)
        # self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        # self.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
        # self.setDropIndicatorShown(True)

        # root = self.invisibleRootItem()
        # root.setFlags(root.flags() & ~QtCore.Qt.ItemIsDropEnabled)

        self.annotation_items = []
        self.groups = {}

        self.root_item_font = QtGui.QFont()
        self.root_item_font.setWeight(QtGui.QFont.Bold)
        self.root_item_font.setPointSize(10)

    def set_model(self, model: SigMFModel):
        # Clean widget
        self.clear()
        self.model = model

        for group in self.model.groups.groups:
            group_item = self.create_group_item(group)
            self.groups[group] = group_item

        # We create a group for annotations without group
        self.groups[None] = self.create_group_item("Ungrouped")

        self.addTopLevelItems(list(self.groups.values()))

        # Add every annotation in the model to the view
        for annotation in self.model.annotations:
            self.add_annotation(annotation)

        # Add new annotation every time a new annotation is added to the model
        self.model.annotation_added.connect(self.add_annotation)
        self.model.annotation_removed.connect(self.remove_annotation)

    def create_group_item(self, group_label):
        new_group_item = QtWidgets.QTreeWidgetItem(self)
        new_group_item.setText(0, group_label)
        new_group_item.setFont(0, self.root_item_font)
        new_group_item.setBackground(0, self.palette().brush(QtGui.QPalette.Normal, QtGui.QPalette.Dark))
        new_group_item.setFirstColumnSpanned(True)
        new_group_item.setFlags(new_group_item.flags() & ~QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
        new_group_item.setExpanded(True)
        return new_group_item

    @QtCore.Slot(object)
    def add_annotation(self, annotation: Annotation):
        logging.debug("Adding annotation to TreeView")
        annotation_item = AnnotationTreeItem(annotation)

        annotation_label_combobox = QtWidgets.QComboBox(self)
        annotation_label_combobox.setModel(self.model.labels)
        annotation_label_combobox.setModelColumn(0)
        annotation_label_combobox.setEditable(True)

        self.setItemWidget(annotation_item.label_item, 1, annotation_label_combobox)

        annotation_item.label_item.setFlags(annotation_item.label_item.flags() | QtCore.Qt.ItemIsSelectable)

        if annotation.label:
            annotation_label_combobox.setCurrentText(annotation.label)
        else:
            annotation_label_combobox.setCurrentIndex(-1)

        annotation_label_combobox.currentIndexChanged.connect(
            lambda idx:
                self.update_annotation_label(
                    annotation_label_combobox.itemText(idx),
                    annotation
                )
        )

        # Add group to tree view
        if annotation.group not in self.groups.keys():
            new_group = self.create_group_item(annotation.group)
            self.groups[annotation.group] = new_group
            self.addTopLevelItem(new_group)

        self.groups[annotation.group].addChild(annotation_item)

        annotation.annotation_changed.connect(self.update_annotation)
        annotation.annotation_selected.connect(self.select_annotation)

    @QtCore.Slot(object)
    def remove_annotation(self, annotation: Annotation):
        for item_idx in range(self.groups[annotation.group].childCount()):
            item = self.groups[annotation.group].child(item_idx)
            if item.annotation == annotation:
                self.groups[annotation.group].removeChild(item)
                break

    @QtCore.Slot(object)
    def update_annotation(self, annotation: Annotation):
        # Find the updated annotation
        for group_key, group_item in self.groups.items():
            for item_idx in range(group_item.childCount()):
                item = group_item.child(item_idx)
                if item.annotation == annotation:
                    if annotation.group != group_key:
                        # Changed groups
                        group_item.removeChild(item)
                        if annotation.group not in self.groups.keys():
                            #New group
                            new_group = self.create_group_item(annotation.group)
                            new_group.addChild(item)
                            self.groups[annotation.group] = new_group
                            self.addTopLevelItems(self.groups.values())
                        else:
                            # Add to group
                            self.groups[annotation.group].addChild(item)
                    else:
                        # Group did not changed
                        pass
                    # Update annotation item
                    item.update_annotation_data()
                    self.itemWidget(item.label_item, 1).setCurrentText(annotation.label)
                    return

        logging.warning(f"Updated annotation at {annotation.start} not found in the tree view")

    @QtCore.Slot(object)
    def select_annotation(self, annotation: Annotation):
        for item_idx in range(self.groups[annotation.group].childCount()):
            item = self.groups[annotation.group].child(item_idx)
            if item.annotation == annotation:
                item.setExpanded(annotation.selected)
                # item.setSelected(annotation.selected)
                break

    def change_annotation_label(self, edit: QtWidgets.QLineEdit, annotation: Annotation):
        label_text = edit.text()
        if label_text and label_text not in self.model.labels.stringList():
            res = QtWidgets.QMessageBox.question(self, "Add label", f"Do you want to add {label_text} to the model?")
            if res == QtWidgets.QMessageBox.Yes:
                logging.debug(f"Adding label {label_text} to model")
                self.model.labels.setStringList(self.model.labels.stringList() + [label_text])
            else:
                pass
        annotation.label = label_text
        annotation.annotation_changed.emit(annotation)

    # def startDrag(self, supportedActions: typing.Union[QtCore.Qt.DropActions, QtCore.Qt.DropAction]) -> None:
    #     print(f"Drag start with {len(self.selectedItems())} items")
    #     super().startDrag(supportedActions)
    #
    # def dropEvent(self, event: QtGui.QDropEvent) -> None:
    #     item = self.itemAt(event.pos())
    #     if item.parent():
    #         item = item.parent()
    #     print(f"Drop at {item.text(0)}")
    #     super().dropEvent(event)

    def update_annotation_label(self, label, annotation: Annotation):
        logging.debug(f"Change annotation label from {annotation.label} to {label}")
        annotation.label = label
        annotation.annotation_changed.emit(annotation)
