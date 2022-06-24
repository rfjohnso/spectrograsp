import logging
from PySide6 import QtCore, QtWidgets, QtGui

from sigmf_model import SigMFModel
from labels_table_view import LabelsViewLayout
from groups_list_view import GroupsViewLayout

from ui.ui_sigmf_dialog import Ui_sigmf_dialog


class SigMFDialog(QtWidgets.QDialog):

    DIALOG_TITLE = "SigMF Archive"

    def __init__(self, parent=None):
        super(SigMFDialog, self).__init__(parent)
        self.ui = Ui_sigmf_dialog()

        self.labels_view_layout = LabelsViewLayout()
        self.groups_view_layout = GroupsViewLayout()

        self.ui.setupUi(self)

    def set_model(self, model: SigMFModel):

        self.model = model

        self.setWindowTitle(f"{self.DIALOG_TITLE} - {self.model.file_name}")

        self.ui.sigmf_dialog_archive_lineedit_value.setText(str(self.model.file_name))
        self.ui.sigmf_dialog_sample_count_label_value.setText(f"{self.model.get_sample_count()} samples")
        self.ui.sigmf_dialog_sampling_frequency_label_value.setText(f"{self.model.get_sample_rate()} Hz")
        self.ui.sigmf_dialog_version_label_value.setText(f"{self.model.sigmf_file.version}")

        self.ui.sigmf_dialog_sample_format_label_value.setText(str(self.model.get_format()))

        self.ui.sigmf_dialog_author_label_value.setText(str(self.model.get_author()))
        self.ui.sigmf_dialog_description_label_value.setText(str(self.model.get_description()))

        self.ui.sigmf_dialog_capture_combobox_value.clear()
        self.ui.sigmf_dialog_capture_combobox_value.addItems(
            [f"Capture {n}" for n in range(len(self.model))])
        # SigMF metadata has to have at least one capture
        self.ui.sigmf_dialog_capture_combobox_value.currentIndexChanged.connect(self.change_capture)
        self.ui.sigmf_dialog_capture_combobox_value.setCurrentIndex(0)

        self.labels_view_layout.set_model(self.model.labels)
        self.ui.sigmf_dialog_labels_groupbox.setLayout(self.labels_view_layout)

        self.groups_view_layout.set_model(self.model.groups)
        self.ui.sigmf_dialog_groups_groupbox.setLayout(self.groups_view_layout)


    @QtCore.Slot()
    def change_capture(self, idx):
        if idx > 0:
            print(f"Capture changed to {idx}")
            self.model.capture = idx
            self.ui.sigmf_dialog_capture_center_frequency_label_value.setText(f"{self.model.get_central_frequency()} Hz")

        else:
            pass

