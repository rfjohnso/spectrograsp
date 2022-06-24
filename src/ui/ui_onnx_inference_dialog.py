# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'onnx_inference_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QGridLayout, QGroupBox, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QSplitter, QTableView, QVBoxLayout, QWidget)

class Ui_onnx_inference_dialog(object):
    def setupUi(self, onnx_inference_dialog):
        if not onnx_inference_dialog.objectName():
            onnx_inference_dialog.setObjectName(u"onnx_inference_dialog")
        onnx_inference_dialog.resize(640, 480)
        self.verticalLayout = QVBoxLayout(onnx_inference_dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(onnx_inference_dialog)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.groupBox = QGroupBox(self.splitter)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(0, 0))
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.open_model_button = QPushButton(self.groupBox)
        self.open_model_button.setObjectName(u"open_model_button")

        self.verticalLayout_3.addWidget(self.open_model_button)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setContentsMargins(6, 6, 6, 6)
        self.model_producer_value = QLabel(self.groupBox)
        self.model_producer_value.setObjectName(u"model_producer_value")

        self.gridLayout.addWidget(self.model_producer_value, 9, 1, 1, 1)

        self.model_name_value = QLabel(self.groupBox)
        self.model_name_value.setObjectName(u"model_name_value")

        self.gridLayout.addWidget(self.model_name_value, 1, 1, 1, 1)

        self.model_name_label = QLabel(self.groupBox)
        self.model_name_label.setObjectName(u"model_name_label")

        self.gridLayout.addWidget(self.model_name_label, 1, 0, 1, 1)

        self.model_file_value = QLabel(self.groupBox)
        self.model_file_value.setObjectName(u"model_file_value")
        self.model_file_value.setScaledContents(False)
        self.model_file_value.setWordWrap(False)

        self.gridLayout.addWidget(self.model_file_value, 0, 1, 1, 1)

        self.model_output_shape_value = QLabel(self.groupBox)
        self.model_output_shape_value.setObjectName(u"model_output_shape_value")

        self.gridLayout.addWidget(self.model_output_shape_value, 7, 1, 1, 1)

        self.model_version_value = QLabel(self.groupBox)
        self.model_version_value.setObjectName(u"model_version_value")

        self.gridLayout.addWidget(self.model_version_value, 2, 1, 1, 1)

        self.model_output_type_value = QLabel(self.groupBox)
        self.model_output_type_value.setObjectName(u"model_output_type_value")

        self.gridLayout.addWidget(self.model_output_type_value, 8, 1, 1, 1)

        self.model_output_value = QLabel(self.groupBox)
        self.model_output_value.setObjectName(u"model_output_value")

        self.gridLayout.addWidget(self.model_output_value, 6, 1, 1, 1)

        self.model_input_value = QLabel(self.groupBox)
        self.model_input_value.setObjectName(u"model_input_value")

        self.gridLayout.addWidget(self.model_input_value, 3, 1, 1, 1)

        self.model_version_label = QLabel(self.groupBox)
        self.model_version_label.setObjectName(u"model_version_label")

        self.gridLayout.addWidget(self.model_version_label, 2, 0, 1, 1)

        self.model_input_type_value = QLabel(self.groupBox)
        self.model_input_type_value.setObjectName(u"model_input_type_value")

        self.gridLayout.addWidget(self.model_input_type_value, 5, 1, 1, 1)

        self.model_hash_label = QLabel(self.groupBox)
        self.model_hash_label.setObjectName(u"model_hash_label")

        self.gridLayout.addWidget(self.model_hash_label, 11, 0, 1, 1)

        self.model_hash_value = QLabel(self.groupBox)
        self.model_hash_value.setObjectName(u"model_hash_value")

        self.gridLayout.addWidget(self.model_hash_value, 11, 1, 1, 1)

        self.model_input_shape_value = QLabel(self.groupBox)
        self.model_input_shape_value.setObjectName(u"model_input_shape_value")

        self.gridLayout.addWidget(self.model_input_shape_value, 4, 1, 1, 1)

        self.model_output_label = QLabel(self.groupBox)
        self.model_output_label.setObjectName(u"model_output_label")

        self.gridLayout.addWidget(self.model_output_label, 6, 0, 1, 1)

        self.model_input_label = QLabel(self.groupBox)
        self.model_input_label.setObjectName(u"model_input_label")

        self.gridLayout.addWidget(self.model_input_label, 3, 0, 1, 1)

        self.model_file_label = QLabel(self.groupBox)
        self.model_file_label.setObjectName(u"model_file_label")

        self.gridLayout.addWidget(self.model_file_label, 0, 0, 1, 1)

        self.model_producer_label = QLabel(self.groupBox)
        self.model_producer_label.setObjectName(u"model_producer_label")

        self.gridLayout.addWidget(self.model_producer_label, 9, 0, 1, 1)

        self.model_domain_label = QLabel(self.groupBox)
        self.model_domain_label.setObjectName(u"model_domain_label")

        self.gridLayout.addWidget(self.model_domain_label, 10, 0, 1, 1)

        self.model_domain_value = QLabel(self.groupBox)
        self.model_domain_value.setObjectName(u"model_domain_value")

        self.gridLayout.addWidget(self.model_domain_value, 10, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.splitter.addWidget(self.groupBox)
        self.groupBox_2 = QGroupBox(self.splitter)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setMaximumSize(QSize(300, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.open_labels_button = QPushButton(self.groupBox_2)
        self.open_labels_button.setObjectName(u"open_labels_button")

        self.verticalLayout_2.addWidget(self.open_labels_button)

        self.labels_tableview = QTableView(self.groupBox_2)
        self.labels_tableview.setObjectName(u"labels_tableview")
        self.labels_tableview.setAlternatingRowColors(True)
        self.labels_tableview.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.labels_tableview.setTextElideMode(Qt.ElideNone)
        self.labels_tableview.setSortingEnabled(False)
        self.labels_tableview.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_2.addWidget(self.labels_tableview)

        self.splitter.addWidget(self.groupBox_2)

        self.verticalLayout.addWidget(self.splitter)

        self.buttonBox = QDialogButtonBox(onnx_inference_dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(onnx_inference_dialog)
        self.buttonBox.accepted.connect(onnx_inference_dialog.accept)
        self.buttonBox.rejected.connect(onnx_inference_dialog.reject)

        QMetaObject.connectSlotsByName(onnx_inference_dialog)
    # setupUi

    def retranslateUi(self, onnx_inference_dialog):
        onnx_inference_dialog.setWindowTitle(QCoreApplication.translate("onnx_inference_dialog", u"ONNX inference", None))
        self.groupBox.setTitle(QCoreApplication.translate("onnx_inference_dialog", u"ONNX Model", None))
        self.open_model_button.setText(QCoreApplication.translate("onnx_inference_dialog", u"Open ONNX model", None))
        self.model_producer_value.setText("")
        self.model_name_value.setText("")
        self.model_name_label.setText(QCoreApplication.translate("onnx_inference_dialog", u"Model name:", None))
        self.model_file_value.setText("")
        self.model_output_shape_value.setText("")
        self.model_version_value.setText("")
        self.model_output_type_value.setText("")
        self.model_output_value.setText("")
        self.model_input_value.setText("")
        self.model_version_label.setText(QCoreApplication.translate("onnx_inference_dialog", u"Model version:", None))
        self.model_input_type_value.setText("")
        self.model_hash_label.setText(QCoreApplication.translate("onnx_inference_dialog", u"MD5 hash:", None))
        self.model_hash_value.setText("")
        self.model_input_shape_value.setText("")
        self.model_output_label.setText(QCoreApplication.translate("onnx_inference_dialog", u"Output:", None))
        self.model_input_label.setText(QCoreApplication.translate("onnx_inference_dialog", u"Input:", None))
        self.model_file_label.setText(QCoreApplication.translate("onnx_inference_dialog", u"Model file:", None))
        self.model_producer_label.setText(QCoreApplication.translate("onnx_inference_dialog", u"Producer:", None))
        self.model_domain_label.setText(QCoreApplication.translate("onnx_inference_dialog", u"Domain:", None))
        self.model_domain_value.setText("")
        self.groupBox_2.setTitle(QCoreApplication.translate("onnx_inference_dialog", u"Labels", None))
        self.open_labels_button.setText(QCoreApplication.translate("onnx_inference_dialog", u"Open label file", None))
    # retranslateUi

