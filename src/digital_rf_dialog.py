import logging
from PySide6 import QtCore, QtWidgets, QtGui

from digitalrf_model import DigitalRFModel
from labels_table_view import LabelsViewLayout
from groups_list_view import GroupsViewLayout

from ui.ui_digital_rf_dialog import Ui_digitalrf_dialog


class DigitalRFDialog(QtWidgets.QDialog):

    DIALOG_TITLE = "Digital RF"

    def __init__(self, parent=None):
        super(DigitalRFDialog, self).__init__(parent)
        self.ui = Ui_digitalrf_dialog()

        self.labels_view_layout = LabelsViewLayout()
        self.groups_view_layout = GroupsViewLayout()

        self.ui.setupUi(self)

        # Dirty hack to disable user input in the checkboxes
        self.ui.digitalrf_dialog_checkbox_continous.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.ui.digitalrf_dialog_checkbox_complex.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

    def set_model(self, model: DigitalRFModel):

        self.model = model

        self.setWindowTitle(f"{self.DIALOG_TITLE} - {self.model.channel_path}")

        self.ui.digitalrf_dialog_lineedit_channel_folder.setText(str(self.model.channel_path))

        self.ui.digitalrf_dialog_buttonbox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)

        self.ui.digitalrf_dialog_label_sampling_rate_value.setText(f"{self.model.get_sample_rate()} Hz")
        self.ui.digitalrf_dialog_label_num_samples_value.setText(f"{self.model.get_sample_count()} samples")

        # Not the best way to access these properties
        channel_properties = self.model.digitalrf_data.get_properties(self.model.get_channel())

        if channel_properties['is_continuous']:
            self.ui.digitalrf_dialog_checkbox_continous.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.ui.digitalrf_dialog_checkbox_continous.setCheckState(QtCore.Qt.CheckState.Unchecked)

        if channel_properties['is_complex']:
            self.ui.digitalrf_dialog_checkbox_complex.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.ui.digitalrf_dialog_checkbox_complex.setCheckState(QtCore.Qt.CheckState.Unchecked)

        self.ui.digitalrf_dialog_label_precision_value.setText(str(channel_properties['H5Tget_precision']))
        self.ui.digitalrf_dialog_label_drf_version_value.setText(channel_properties['digital_rf_version'])

        self.ui.digitalrf_dialog_combobox_subchannel.clear()
        self.ui.digitalrf_dialog_combobox_subchannel.addItems(
            [f"Subchannel {n}" for n in range(channel_properties['num_subchannels'])])

        if self.model.metadata_path:
            self.ui.digitalrf_dialog_lineedit_metadata_folder.setText(str(self.model.metadata_path))
            self.ui.digitalrf_dialog_label_annotation_count_value.setText(str(len(self.model.annotations)))
            self.ui.digitalrf_dialog_label_label_count_value.setText(str(len(self.model.labels.labels)))
            self.ui.digitalrf_dialog_label_group_count_value.setText(str(len(self.model.groups.groups)))
        else:
            self.ui.digitalrf_dialog_buttonbox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

        self.ui.digitalrf_dialog_button_select_metadata_folder.clicked.connect(self.select_metadata)

        # if channel_properties['is_continuous']:
        #     self.ui.digitalrf_dialog_buttonbox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        # else:
        #     # TODO: Add support for not continuous digital rf data
        #     self.ui.digitalrf_dialog_buttonbox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

        self.labels_view_layout.set_model(self.model.labels)
        self.ui.digitalrf_dialog_labels_groupbox.setLayout(self.labels_view_layout)

        self.groups_view_layout.set_model(self.model.groups)
        self.ui.digitalrf_dialog_groups_groupbox.setLayout(self.groups_view_layout)

        self.ui.digitalrf_dialog_combobox_subchannel.currentIndexChanged.connect(self.change_subchannel)

    @QtCore.Slot()
    def change_subchannel(self, idx):
        if idx > 0:
            print(f"Subchannel changed to {idx}")
            self.model.set_sub_channel(idx)

    @QtCore.Slot()
    def select_metadata(self):

        metadata_properties = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                    "Digital RF metadata",
                                                                    "/",
                                                                    "Digital RF metadata (dmd_properties.h5)")
