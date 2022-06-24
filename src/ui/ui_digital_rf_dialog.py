# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'digital_rf_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.2.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QSplitter,
    QVBoxLayout, QWidget)

class Ui_digitalrf_dialog(object):
    def setupUi(self, digitalrf_dialog):
        if not digitalrf_dialog.objectName():
            digitalrf_dialog.setObjectName(u"digitalrf_dialog")
        digitalrf_dialog.setWindowModality(Qt.WindowModal)
        digitalrf_dialog.resize(832, 583)
        digitalrf_dialog.setSizeGripEnabled(True)
        digitalrf_dialog.setModal(True)
        self.verticalLayout = QVBoxLayout(digitalrf_dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(digitalrf_dialog)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setHandleWidth(20)
        self.digitalrf_dialog_right_widget = QWidget(self.splitter)
        self.digitalrf_dialog_right_widget.setObjectName(u"digitalrf_dialog_right_widget")
        self.gridLayout = QGridLayout(self.digitalrf_dialog_right_widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(6)
        self.digitalrf_dialog_label_label_count_name = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_label_count_name.setObjectName(u"digitalrf_dialog_label_label_count_name")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_label_count_name, 14, 2, 1, 1)

        self.digitalrf_dialog_label_num_samples_name = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_num_samples_name.setObjectName(u"digitalrf_dialog_label_num_samples_name")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_num_samples_name, 3, 2, 1, 1)

        self.digitalrf_dialog_label_drf_version_name = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_drf_version_name.setObjectName(u"digitalrf_dialog_label_drf_version_name")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_drf_version_name, 5, 2, 1, 1)

        self.digitalrf_dialog_button_select_metadata_folder = QPushButton(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_button_select_metadata_folder.setObjectName(u"digitalrf_dialog_button_select_metadata_folder")
        self.digitalrf_dialog_button_select_metadata_folder.setEnabled(False)

        self.gridLayout.addWidget(self.digitalrf_dialog_button_select_metadata_folder, 12, 4, 1, 1)

        self.digitalrf_dialog_label_precision_name = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_precision_name.setObjectName(u"digitalrf_dialog_label_precision_name")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_precision_name, 4, 2, 1, 1)

        self.digitalrf_dialog_label_subchannel_name = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_subchannel_name.setObjectName(u"digitalrf_dialog_label_subchannel_name")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_subchannel_name, 10, 2, 1, 1)

        self.line = QFrame(self.digitalrf_dialog_right_widget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 11, 3, 1, 2)

        self.digitalrf_dialog_label_group_count_value = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_group_count_value.setObjectName(u"digitalrf_dialog_label_group_count_value")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_group_count_value, 15, 3, 1, 1)

        self.digitalrf_dialog_label_drf_version_value = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_drf_version_value.setObjectName(u"digitalrf_dialog_label_drf_version_value")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_drf_version_value, 5, 3, 1, 1)

        self.digitalrf_dialog_combobox_subchannel = QComboBox(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_combobox_subchannel.setObjectName(u"digitalrf_dialog_combobox_subchannel")

        self.gridLayout.addWidget(self.digitalrf_dialog_combobox_subchannel, 10, 3, 1, 1)

        self.digitalrf_dialog_lineedit_channel_folder = QLineEdit(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_lineedit_channel_folder.setObjectName(u"digitalrf_dialog_lineedit_channel_folder")

        self.gridLayout.addWidget(self.digitalrf_dialog_lineedit_channel_folder, 1, 3, 1, 2)

        self.digitalrf_dialog_label_num_samples_value = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_num_samples_value.setObjectName(u"digitalrf_dialog_label_num_samples_value")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_num_samples_value, 3, 3, 1, 1)

        self.digitalrf_dialog_label_precision_value = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_precision_value.setObjectName(u"digitalrf_dialog_label_precision_value")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_precision_value, 4, 3, 1, 1)

        self.digitalrf_dialog_label_label_count_value = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_label_count_value.setObjectName(u"digitalrf_dialog_label_label_count_value")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_label_count_value, 14, 3, 1, 1)

        self.digitalrf_dialog_label_sampling_rate_value = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_sampling_rate_value.setObjectName(u"digitalrf_dialog_label_sampling_rate_value")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_sampling_rate_value, 2, 3, 1, 1)

        self.digitalrf_dialog_label_annotation_count_value = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_annotation_count_value.setObjectName(u"digitalrf_dialog_label_annotation_count_value")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_annotation_count_value, 13, 3, 1, 1)

        self.digitalrf_dialog_label_sampling_rate_name = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_sampling_rate_name.setObjectName(u"digitalrf_dialog_label_sampling_rate_name")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_sampling_rate_name, 2, 2, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.digitalrf_dialog_checkbox_continous = QCheckBox(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_checkbox_continous.setObjectName(u"digitalrf_dialog_checkbox_continous")
        self.digitalrf_dialog_checkbox_continous.setFocusPolicy(Qt.NoFocus)
        self.digitalrf_dialog_checkbox_continous.setCheckable(True)

        self.horizontalLayout.addWidget(self.digitalrf_dialog_checkbox_continous)

        self.digitalrf_dialog_checkbox_complex = QCheckBox(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_checkbox_complex.setObjectName(u"digitalrf_dialog_checkbox_complex")
        self.digitalrf_dialog_checkbox_complex.setFocusPolicy(Qt.NoFocus)
        self.digitalrf_dialog_checkbox_complex.setCheckable(True)
        self.digitalrf_dialog_checkbox_complex.setChecked(False)
        self.digitalrf_dialog_checkbox_complex.setAutoRepeat(False)

        self.horizontalLayout.addWidget(self.digitalrf_dialog_checkbox_complex)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout, 9, 3, 1, 1)

        self.digitalrf_dialog_label_channel_folder_name = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_channel_folder_name.setObjectName(u"digitalrf_dialog_label_channel_folder_name")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_channel_folder_name, 1, 2, 1, 1)

        self.digitalrf_dialog_label_annotation_count_name = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_annotation_count_name.setObjectName(u"digitalrf_dialog_label_annotation_count_name")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_annotation_count_name, 13, 2, 1, 1)

        self.digitalrf_dialog_label_group_count_name = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_group_count_name.setObjectName(u"digitalrf_dialog_label_group_count_name")

        self.gridLayout.addWidget(self.digitalrf_dialog_label_group_count_name, 15, 2, 1, 1)

        self.digitalrf_dialog_lineedit_metadata_folder = QLineEdit(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_lineedit_metadata_folder.setObjectName(u"digitalrf_dialog_lineedit_metadata_folder")
        self.digitalrf_dialog_lineedit_metadata_folder.setFocusPolicy(Qt.NoFocus)
        self.digitalrf_dialog_lineedit_metadata_folder.setReadOnly(True)

        self.gridLayout.addWidget(self.digitalrf_dialog_lineedit_metadata_folder, 12, 3, 1, 1)

        self.digitalrf_dialog_label_metadata_folder = QLabel(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_label_metadata_folder.setObjectName(u"digitalrf_dialog_label_metadata_folder")
        self.digitalrf_dialog_label_metadata_folder.setTextFormat(Qt.MarkdownText)
        self.digitalrf_dialog_label_metadata_folder.setScaledContents(False)
        self.digitalrf_dialog_label_metadata_folder.setWordWrap(True)

        self.gridLayout.addWidget(self.digitalrf_dialog_label_metadata_folder, 12, 2, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 16, 2, 1, 3)

        self.splitter.addWidget(self.digitalrf_dialog_right_widget)
        self.digitalrf_dialog_left_widget = QWidget(self.splitter)
        self.digitalrf_dialog_left_widget.setObjectName(u"digitalrf_dialog_left_widget")
        self.digitalrf_dialog_left_widget.setMinimumSize(QSize(250, 0))
        self.digitalrf_dialog_left_widget.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.digitalrf_dialog_left_widget)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.digitalrf_dialog_labels_groupbox = QGroupBox(self.digitalrf_dialog_left_widget)
        self.digitalrf_dialog_labels_groupbox.setObjectName(u"digitalrf_dialog_labels_groupbox")

        self.verticalLayout_2.addWidget(self.digitalrf_dialog_labels_groupbox)

        self.digitalrf_dialog_groups_groupbox = QGroupBox(self.digitalrf_dialog_left_widget)
        self.digitalrf_dialog_groups_groupbox.setObjectName(u"digitalrf_dialog_groups_groupbox")
        self.digitalrf_dialog_groups_groupbox.setMinimumSize(QSize(0, 0))

        self.verticalLayout_2.addWidget(self.digitalrf_dialog_groups_groupbox)

        self.splitter.addWidget(self.digitalrf_dialog_left_widget)

        self.verticalLayout.addWidget(self.splitter)

        self.digitalrf_dialog_buttonbox = QDialogButtonBox(digitalrf_dialog)
        self.digitalrf_dialog_buttonbox.setObjectName(u"digitalrf_dialog_buttonbox")
        self.digitalrf_dialog_buttonbox.setOrientation(Qt.Horizontal)
        self.digitalrf_dialog_buttonbox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.digitalrf_dialog_buttonbox)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 2)
        QWidget.setTabOrder(self.digitalrf_dialog_combobox_subchannel, self.digitalrf_dialog_lineedit_metadata_folder)
        QWidget.setTabOrder(self.digitalrf_dialog_lineedit_metadata_folder, self.digitalrf_dialog_button_select_metadata_folder)

        self.retranslateUi(digitalrf_dialog)
        self.digitalrf_dialog_buttonbox.accepted.connect(digitalrf_dialog.accept)
        self.digitalrf_dialog_buttonbox.rejected.connect(digitalrf_dialog.reject)

        QMetaObject.connectSlotsByName(digitalrf_dialog)
    # setupUi

    def retranslateUi(self, digitalrf_dialog):
        digitalrf_dialog.setWindowTitle(QCoreApplication.translate("digitalrf_dialog", u"Digital RF", None))
        self.digitalrf_dialog_label_label_count_name.setText(QCoreApplication.translate("digitalrf_dialog", u"Label count", None))
        self.digitalrf_dialog_label_num_samples_name.setText(QCoreApplication.translate("digitalrf_dialog", u"Num samples", None))
        self.digitalrf_dialog_label_drf_version_name.setText(QCoreApplication.translate("digitalrf_dialog", u"Digital RF version", None))
        self.digitalrf_dialog_button_select_metadata_folder.setText(QCoreApplication.translate("digitalrf_dialog", u"Select", None))
        self.digitalrf_dialog_label_precision_name.setText(QCoreApplication.translate("digitalrf_dialog", u"Precision", None))
        self.digitalrf_dialog_label_subchannel_name.setText(QCoreApplication.translate("digitalrf_dialog", u"Subchannel", None))
        self.digitalrf_dialog_label_group_count_value.setText("")
        self.digitalrf_dialog_label_drf_version_value.setText("")
        self.digitalrf_dialog_label_num_samples_value.setText("")
        self.digitalrf_dialog_label_precision_value.setText("")
        self.digitalrf_dialog_label_label_count_value.setText("")
        self.digitalrf_dialog_label_sampling_rate_value.setText("")
        self.digitalrf_dialog_label_annotation_count_value.setText("")
        self.digitalrf_dialog_label_sampling_rate_name.setText(QCoreApplication.translate("digitalrf_dialog", u"Sampling rate", None))
        self.digitalrf_dialog_checkbox_continous.setText(QCoreApplication.translate("digitalrf_dialog", u"Continuos", None))
        self.digitalrf_dialog_checkbox_complex.setText(QCoreApplication.translate("digitalrf_dialog", u"Complex", None))
        self.digitalrf_dialog_label_channel_folder_name.setText(QCoreApplication.translate("digitalrf_dialog", u"Channel folder", None))
        self.digitalrf_dialog_label_annotation_count_name.setText(QCoreApplication.translate("digitalrf_dialog", u"Annotation count", None))
        self.digitalrf_dialog_label_group_count_name.setText(QCoreApplication.translate("digitalrf_dialog", u"Group count", None))
        self.digitalrf_dialog_label_metadata_folder.setText(QCoreApplication.translate("digitalrf_dialog", u"Metadata folder", None))
        self.digitalrf_dialog_labels_groupbox.setTitle(QCoreApplication.translate("digitalrf_dialog", u"Labels", None))
        self.digitalrf_dialog_groups_groupbox.setTitle(QCoreApplication.translate("digitalrf_dialog", u"Groups", None))
    # retranslateUi

