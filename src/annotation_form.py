import logging

from PySide6 import QtCore, QtWidgets

from data_model import DataModel
from annotation import Annotation


class AnnotationForm(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(AnnotationForm, self).__init__(parent)
        self.setupUI()

        self.default_label = ""
        self.default_group = ""

    def setupUI(self):
        main_layout = QtWidgets.QFormLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        start_label = QtWidgets.QLabel("Start")
        self.start_edit = QtWidgets.QLineEdit()
        self.start_edit.setReadOnly(True)
        self.start_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        length_label = QtWidgets.QLabel("Length")
        self.length_edit = QtWidgets.QLineEdit()
        self.length_edit.setReadOnly(True)
        self.length_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        low_freq_label = QtWidgets.QLabel("Low freq.")
        self.low_freq_edit = QtWidgets.QLineEdit()
        self.low_freq_edit.setReadOnly(True)
        self.low_freq_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        high_freq_label = QtWidgets.QLabel("High freq.")
        self.high_freqh_edit = QtWidgets.QLineEdit()
        self.high_freqh_edit.setReadOnly(True)
        self.high_freqh_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        author_label = QtWidgets.QLabel("Author")
        self.author_edit = QtWidgets.QLineEdit()

        comment_label = QtWidgets.QLabel("Comment")
        self.comment_edit = QtWidgets.QLineEdit()

        symbol_rate_label = QtWidgets.QLabel("Symbol rate")
        self.symbol_rate_edit = QtWidgets.QLineEdit()
        self.symbol_rate_edit.setReadOnly(True)
        self.symbol_rate_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        group_label = QtWidgets.QLabel("Group")
        self.group_combobox = QtWidgets.QComboBox()
        self.group_combobox.setEditable(True)

        label_label = QtWidgets.QLabel("Label")
        self.label_combobox = QtWidgets.QComboBox()
        self.label_combobox.setEditable(True)

        confindence_label = QtWidgets.QLabel("Confidence")
        self.confidence_spingbox = QtWidgets.QDoubleSpinBox()
        self.confidence_spingbox.setMaximum(100.0)
        self.confidence_spingbox.setMinimum(0.0)
        self.confidence_spingbox.setSingleStep(1.0)
        self.confidence_spingbox.setSuffix("%")


        main_layout.addRow(start_label, self.start_edit)
        main_layout.addRow(length_label, self.length_edit)
        main_layout.addRow(low_freq_label, self.low_freq_edit)
        main_layout.addRow(high_freq_label, self.high_freqh_edit)
        main_layout.addRow(author_label, self.author_edit)
        main_layout.addRow(comment_label, self.comment_edit)
        main_layout.addRow(symbol_rate_label, self.symbol_rate_edit)
        main_layout.addRow(group_label, self.group_combobox)
        main_layout.addRow(label_label, self.label_combobox)
        main_layout.addRow(confindence_label, self.confidence_spingbox)

        self.setLayout(main_layout)

    def set_model(self, model: DataModel):
        self.model = model

        self.label_combobox.setModel(self.model.labels)
        self.label_combobox.setCurrentIndex(-1)

        label_completer = QtWidgets.QCompleter(self.model.labels, self)
        label_completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

        self.label_combobox.setCompleter(label_completer)

        self.group_combobox.setModel(self.model.groups)
        self.group_combobox.setCurrentIndex(-1)

        group_completer = QtWidgets.QCompleter(self.model.groups, self)
        group_completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        # self.label_completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
        self.group_combobox.setCompleter(group_completer)

    def set_annotation(self, annotation: Annotation):
        self.annotation = annotation
        self.fill_form_data(self.annotation)
        self.annotation.annotation_changed.connect(self.fill_form_data)
        # TODO: Save changes on request and not by default
        self.author_edit.editingFinished.connect(self.author_changed)
        self.comment_edit.editingFinished.connect(self.comment_changed)
        self.label_combobox.lineEdit().editingFinished.connect(self.label_changed)
        self.group_combobox.lineEdit().editingFinished.connect(self.group_changed)
        self.label_combobox.lineEdit().returnPressed.connect(self.label_changed)
        self.confidence_spingbox.lineEdit().editingFinished.connect(self.confidence_changed)

    def fill_form_data(self, annotation: Annotation):
        self.start_edit.setText(f"{annotation.start:.02f} s")
        self.length_edit.setText(f"{annotation.length:.02f} s")
        self.low_freq_edit.setText(f"{annotation.low:.02f} Hz")
        self.high_freqh_edit.setText(f"{annotation.high:.02f} Hz")
        self.author_edit.setText(f"{annotation.metadata.get('author','')}")
        self.comment_edit.setText(f"{annotation.metadata.get('comment', '')}")
        self.symbol_rate_edit.setText(f"{annotation.metadata.get('symbol_rate','')} Sym/s")
        self.label_combobox.setCurrentText(f"{annotation.label if annotation.label else ''}")
        self.group_combobox.setCurrentText(f"{annotation.group if annotation.group else ''}")
        self.confidence_spingbox.setValue(annotation.confidence if annotation.confidence else 0)

    @QtCore.Slot()
    def author_changed(self):
        if self.annotation.author != self.author_edit.text():
            logging.debug(f"Author changed: {self.author_edit.text()}")
            self.annotation.author = self.author_edit.text()
            self.annotation.annotation_changed.emit(self.annotation)
        else:
            pass

    @QtCore.Slot()
    def comment_changed(self):
        if self.annotation.comment != self.comment_edit.text():
            logging.debug(f"Annotation comment changed: {self.comment_edit.text()}")
            self.annotation.comment = self.comment_edit.text()
            self.annotation.annotation_changed.emit(self.annotation)
        else:
            logging.debug(f"Annotation comment did not changed: {self.annotation.comment}")
            pass

    @QtCore.Slot()
    def label_changed(self):
        if self.annotation.label != self.label_combobox.currentText():
            logging.debug(f"Annotation label changed: {self.annotation.label}")
            if self.label_combobox.currentText():
                self.annotation.label = self.label_combobox.currentText()
                if self.annotation.label not in self.model.labels.labels:
                    res = QtWidgets.QMessageBox.question(self,
                                                         "New label",
                                                         f"Would you like to add {self.annotation.label} to the available labels?")

                    if res == QtWidgets.QMessageBox.Yes:
                        self.model.labels.add_label(self.annotation.label)
                    else:
                        pass
            else:
                logging.debug(f"Removing annotation label")
                self.annotation.label = None
            self.annotation.annotation_changed.emit(self.annotation)
        else:
            logging.debug(f"Annotation label did not changed: {self.annotation.label}")
            pass

    @QtCore.Slot()
    def group_changed(self):
        if self.annotation.group != self.group_combobox.currentText():
            logging.info(f"Annotation group changed: {self.annotation.group}")
            if self.group_combobox.currentText():
                self.annotation.group = self.group_combobox.currentText()
                if self.annotation.group not in self.model.groups.groups:
                    res = QtWidgets.QMessageBox.question(self, "New group",
                                                         f"Would you like to add {self.annotation.group } to the available groups?")
                    if res == QtWidgets.QMessageBox.Yes:
                        self.model.groups.add_group(self.annotation.group)
                    else:
                        pass
            else:
                logging.debug(f"Removing annotation group")
                self.annotation.group = None
            self.annotation.annotation_changed.emit(self.annotation)
        else:
            logging.debug(f"Annotation group did not changed: {self.annotation.group}")
            pass

    @QtCore.Slot()
    def confidence_changed(self):
        self.annotation.confidence = self.confidence_spingbox.value()
        logging.info(f"Annotation confidence changed: {self.annotation.confidence}")
