# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sigmf_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QSizePolicy, QSpacerItem, QSplitter,
    QVBoxLayout, QWidget)

class Ui_sigmf_dialog(object):
    def setupUi(self, sigmf_dialog):
        if not sigmf_dialog.objectName():
            sigmf_dialog.setObjectName(u"sigmf_dialog")
        sigmf_dialog.resize(832, 550)
        font = QFont()
        font.setPointSize(10)
        sigmf_dialog.setFont(font)
        self.verticalLayout = QVBoxLayout(sigmf_dialog)
        self.verticalLayout.setSpacing(7)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(sigmf_dialog)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setHandleWidth(20)
        self.splitter.setChildrenCollapsible(False)
        self.verticalLayoutWidget_2 = QWidget(self.splitter)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.gridLayout = QGridLayout(self.verticalLayoutWidget_2)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.sigmf_dialog_capture_combobox_value = QComboBox(self.verticalLayoutWidget_2)
        self.sigmf_dialog_capture_combobox_value.setObjectName(u"sigmf_dialog_capture_combobox_value")

        self.gridLayout.addWidget(self.sigmf_dialog_capture_combobox_value, 9, 1, 1, 1)

        self.sigmf_dialog_sample_count_label_value = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_sample_count_label_value.setObjectName(u"sigmf_dialog_sample_count_label_value")

        self.gridLayout.addWidget(self.sigmf_dialog_sample_count_label_value, 2, 1, 1, 1)

        self.sigmf_dialog_sampling_frequency_label_name = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_sampling_frequency_label_name.setObjectName(u"sigmf_dialog_sampling_frequency_label_name")

        self.gridLayout.addWidget(self.sigmf_dialog_sampling_frequency_label_name, 3, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 11, 0, 1, 1)

        self.sigmf_dialog_capture_center_frequency_label_name = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_capture_center_frequency_label_name.setObjectName(u"sigmf_dialog_capture_center_frequency_label_name")

        self.gridLayout.addWidget(self.sigmf_dialog_capture_center_frequency_label_name, 10, 0, 1, 1)

        self.sigmf_dialog_capture_label_name = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_capture_label_name.setObjectName(u"sigmf_dialog_capture_label_name")

        self.gridLayout.addWidget(self.sigmf_dialog_capture_label_name, 9, 0, 1, 1)

        self.sigmf_dialog_sample_format_label_value = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_sample_format_label_value.setObjectName(u"sigmf_dialog_sample_format_label_value")

        self.gridLayout.addWidget(self.sigmf_dialog_sample_format_label_value, 4, 1, 1, 1)

        self.sigmf_dialog_author_label_name = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_author_label_name.setObjectName(u"sigmf_dialog_author_label_name")

        self.gridLayout.addWidget(self.sigmf_dialog_author_label_name, 6, 0, 1, 1)

        self.sigmf_dialog_sample_count_label_name = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_sample_count_label_name.setObjectName(u"sigmf_dialog_sample_count_label_name")

        self.gridLayout.addWidget(self.sigmf_dialog_sample_count_label_name, 2, 0, 1, 1)

        self.sigmf_dialog_capture_center_frequency_label_value = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_capture_center_frequency_label_value.setObjectName(u"sigmf_dialog_capture_center_frequency_label_value")

        self.gridLayout.addWidget(self.sigmf_dialog_capture_center_frequency_label_value, 10, 1, 1, 1)

        self.sigmf_dialog_author_label_value = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_author_label_value.setObjectName(u"sigmf_dialog_author_label_value")

        self.gridLayout.addWidget(self.sigmf_dialog_author_label_value, 6, 1, 1, 1)

        self.sigmf_dialog_archive_lineedit_name = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_archive_lineedit_name.setObjectName(u"sigmf_dialog_archive_lineedit_name")

        self.gridLayout.addWidget(self.sigmf_dialog_archive_lineedit_name, 0, 0, 1, 1)

        self.sigmf_dialog_description_label_value = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_description_label_value.setObjectName(u"sigmf_dialog_description_label_value")
        self.sigmf_dialog_description_label_value.setScaledContents(False)
        self.sigmf_dialog_description_label_value.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.sigmf_dialog_description_label_value.setWordWrap(True)
        self.sigmf_dialog_description_label_value.setTextInteractionFlags(Qt.NoTextInteraction)

        self.gridLayout.addWidget(self.sigmf_dialog_description_label_value, 7, 1, 1, 1)

        self.sigmf_dialog_archive_lineedit_value = QLineEdit(self.verticalLayoutWidget_2)
        self.sigmf_dialog_archive_lineedit_value.setObjectName(u"sigmf_dialog_archive_lineedit_value")
        self.sigmf_dialog_archive_lineedit_value.setReadOnly(True)

        self.gridLayout.addWidget(self.sigmf_dialog_archive_lineedit_value, 0, 1, 1, 2)

        self.sigmf_dialog_sampling_frequency_label_value = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_sampling_frequency_label_value.setObjectName(u"sigmf_dialog_sampling_frequency_label_value")

        self.gridLayout.addWidget(self.sigmf_dialog_sampling_frequency_label_value, 3, 1, 1, 1)

        self.sigmf_dialog_sample_format_label_name = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_sample_format_label_name.setObjectName(u"sigmf_dialog_sample_format_label_name")

        self.gridLayout.addWidget(self.sigmf_dialog_sample_format_label_name, 4, 0, 1, 1)

        self.sigmf_dialog_description_label_name = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_description_label_name.setObjectName(u"sigmf_dialog_description_label_name")
        self.sigmf_dialog_description_label_name.setToolTipDuration(1)
        self.sigmf_dialog_description_label_name.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout.addWidget(self.sigmf_dialog_description_label_name, 7, 0, 1, 1)

        self.sigmf_dialog_version_label_name = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_version_label_name.setObjectName(u"sigmf_dialog_version_label_name")

        self.gridLayout.addWidget(self.sigmf_dialog_version_label_name, 5, 0, 1, 1)

        self.sigmf_dialog_version_label_value = QLabel(self.verticalLayoutWidget_2)
        self.sigmf_dialog_version_label_value.setObjectName(u"sigmf_dialog_version_label_value")

        self.gridLayout.addWidget(self.sigmf_dialog_version_label_value, 5, 1, 1, 1)

        self.splitter.addWidget(self.verticalLayoutWidget_2)
        self.widget = QWidget(self.splitter)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(300, 0))
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.sigmf_dialog_labels_groupbox = QGroupBox(self.widget)
        self.sigmf_dialog_labels_groupbox.setObjectName(u"sigmf_dialog_labels_groupbox")

        self.verticalLayout_2.addWidget(self.sigmf_dialog_labels_groupbox)

        self.sigmf_dialog_groups_groupbox = QGroupBox(self.widget)
        self.sigmf_dialog_groups_groupbox.setObjectName(u"sigmf_dialog_groups_groupbox")

        self.verticalLayout_2.addWidget(self.sigmf_dialog_groups_groupbox)

        self.splitter.addWidget(self.widget)

        self.verticalLayout.addWidget(self.splitter)

        self.buttonBox = QDialogButtonBox(sigmf_dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(sigmf_dialog)
        self.buttonBox.accepted.connect(sigmf_dialog.accept)
        self.buttonBox.rejected.connect(sigmf_dialog.reject)

        QMetaObject.connectSlotsByName(sigmf_dialog)
    # setupUi

    def retranslateUi(self, sigmf_dialog):
        sigmf_dialog.setWindowTitle(QCoreApplication.translate("sigmf_dialog", u"Dialog", None))
        self.sigmf_dialog_sample_count_label_value.setText("")
        self.sigmf_dialog_sampling_frequency_label_name.setText(QCoreApplication.translate("sigmf_dialog", u"Sampling frequency:", None))
        self.sigmf_dialog_capture_center_frequency_label_name.setText(QCoreApplication.translate("sigmf_dialog", u"Center frequency:", None))
        self.sigmf_dialog_capture_label_name.setText(QCoreApplication.translate("sigmf_dialog", u"Capture:", None))
        self.sigmf_dialog_sample_format_label_value.setText("")
        self.sigmf_dialog_author_label_name.setText(QCoreApplication.translate("sigmf_dialog", u"Author:", None))
        self.sigmf_dialog_sample_count_label_name.setText(QCoreApplication.translate("sigmf_dialog", u"Sample count:", None))
        self.sigmf_dialog_capture_center_frequency_label_value.setText("")
        self.sigmf_dialog_author_label_value.setText("")
        self.sigmf_dialog_archive_lineedit_name.setText(QCoreApplication.translate("sigmf_dialog", u"SigMF archive:", None))
        self.sigmf_dialog_description_label_value.setText("")
        self.sigmf_dialog_sampling_frequency_label_value.setText("")
        self.sigmf_dialog_sample_format_label_name.setText(QCoreApplication.translate("sigmf_dialog", u"Sample format:", None))
        self.sigmf_dialog_description_label_name.setText(QCoreApplication.translate("sigmf_dialog", u"Description:", None))
        self.sigmf_dialog_version_label_name.setText(QCoreApplication.translate("sigmf_dialog", u"SigMF version:", None))
        self.sigmf_dialog_version_label_value.setText("")
        self.sigmf_dialog_labels_groupbox.setTitle(QCoreApplication.translate("sigmf_dialog", u"Labels", None))
        self.sigmf_dialog_groups_groupbox.setTitle(QCoreApplication.translate("sigmf_dialog", u"Groups", None))
    # retranslateUi

