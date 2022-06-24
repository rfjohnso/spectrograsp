# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)
import resources_rc

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(880, 400)
        AboutDialog.setMinimumSize(QSize(600, 400))
        self.horizontalLayout_2 = QHBoxLayout(AboutDialog)
        self.horizontalLayout_2.setSpacing(20)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(20, 20, 20, 20)
        self.widget = QWidget(AboutDialog)
        self.widget.setObjectName(u"widget")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(250, 75))
        self.label.setPixmap(QPixmap(u":/images/img/heig-vd-2020-reds.png"))
        self.label.setScaledContents(False)

        self.verticalLayout.addWidget(self.label)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.label_3 = QLabel(self.widget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMaximumSize(QSize(250, 125))
        self.label_3.setPixmap(QPixmap(u":/images/img/armasuisse.png"))
        self.label_3.setScaledContents(True)

        self.verticalLayout.addWidget(self.label_3)


        self.horizontalLayout_2.addWidget(self.widget)

        self.label_2 = QLabel(AboutDialog)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setTextFormat(Qt.RichText)
        self.label_2.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.horizontalLayout_2.addWidget(self.label_2)


        self.retranslateUi(AboutDialog)

        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"About", None))
        self.label.setText("")
        self.label_3.setText("")
        self.label_2.setText(QCoreApplication.translate("AboutDialog", u"<html><head/><body><p><span style=\" font-size:20pt; font-weight:600;\">SPECTROGRASP</span></p><p><span style=\" font-size:12pt;\">About spectrograsp</span></p><p><span style=\" font-size:12pt;\">Contact information</span></p><p><span style=\" font-size:12pt;\">Licenses</span></p></body></html>", None))
    # retranslateUi

