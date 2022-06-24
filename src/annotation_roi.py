import logging
from enum import Enum

from PySide6 import QtCore, QtGui, QtWidgets

import pyqtgraph as pg

from annotation import Annotation


class ROIType(Enum):
    COMPLETE = 5


class AnnotationROI(pg.ROI):

    export_roi_signal = QtCore.Signal(object)
    open_roi_signal = QtCore.Signal(object)

    def __init__(self, annotation: Annotation, is_selectable=True, is_time_x_axis=True, **kwargs):

        if annotation.low is None or annotation.high is None:
            logging.error("Annotation empty bandwidth")
            raise ValueError(f"Annotation cannot have empty bandwidth")

        self.annotation = annotation
        self.is_selectable = is_selectable
        self.is_time_x_axis = is_time_x_axis

        if self.is_time_x_axis:
            x = self.annotation.start
            y = self.annotation.low
            w = self.annotation.length
            h = self.annotation.high - self.annotation.low
        else:
            x = self.annotation.low
            y = self.annotation.start
            w = self.annotation.high - self.annotation.low
            h = self.annotation.length

        super(AnnotationROI, self).__init__(pos=(x, y), size=(w, h), **kwargs)

        self.rotatable = False
        self.resizable = True

        # Enable click on ROI
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)

        self.addScaleHandle([0, 0], [1, 1])
        self.addScaleHandle([1, 1], [0, 0])

        # Update annotation only after change event finish
        self.sigRegionChangeFinished.connect(self.region_changed)
        # Connect region clicked with annotation selection
        self.sigClicked.connect(self.region_clicked)
        # Connect annotation selection with visual effects
        self.annotation.annotation_selected.connect(self.select_roi)
        self.annotation.annotation_changed.connect(self.annotation_changed)

        # ROI context menu
        self.menu = None
        # ROI tool top
        self.setToolTip(self.get_tooltip())

    @QtCore.Slot(object)
    def region_changed(self, roi: pg.ROI):
        """
        Capture ROI modification and update annotation accordingly
        :param roi changed ROI
        """
        # print("Region changed", self.pos(), self.size())

        if self.is_time_x_axis:
            x, y = self.pos()
            w, h = self.size()
        else:
            y, x = self.pos()
            h, w = self.size()

        self.annotation.start = x
        self.annotation.length = w
        self.annotation.low = y
        self.annotation.high = y + h

        self.setToolTip(self.get_tooltip())

        self.annotation.annotation_changed.emit(self.annotation)

    @QtCore.Slot(object)
    def annotation_changed(self, annotation):

        if self.is_time_x_axis:
            x = self.annotation.start
            y = self.annotation.low
            w = self.annotation.length
            h = self.annotation.high - self.annotation.low
        else:
            x = self.annotation.low
            y = self.annotation.start
            w = self.annotation.high - self.annotation.low
            h = self.annotation.length

        # Dirty hack to avoid infinite recurrence
        # We modify the view without signaling "sigRegionChangeFinished" because the change comes from the "model"
        self.setPos((x, y), update=False)
        self.setSize((w, h), update=False)
        # We inform the view box about the changes
        self.informViewBoundsChanged()

    @QtCore.Slot()
    def remove_roi(self):
        self.sigRemoveRequested.emit(self)

    @QtCore.Slot()
    def export_roi(self):
        self.export_roi_signal.emit(self.annotation)

    @QtCore.Slot(object, object)
    def region_clicked(self, roi, ev):
        if not ev.double():
            if self.is_selectable:
                self.annotation.selected = not self.annotation.selected
                self.annotation.annotation_selected.emit(self.annotation)
            else:
                pass
        else:
            self.open_roi_signal.emit(self.annotation)

    @QtCore.Slot(object)
    def select_roi(self, annotation):
        if self.annotation.selected:
            logging.debug(f"Selected ROI at ({annotation.start:.2f}, {annotation.length:.2f})")
            # Increase all pen width in selected state
            self.pen.setWidth(self.pen.width() + 2)
            self.hoverPen.setWidth(self.hoverPen.width() + 2)
            self.handlePen.setWidth(self.handlePen.width() + 2)
        else:
            logging.debug(f"Deselected ROI at ({annotation.start:.2f}, {annotation.length:.2f})")
            # Decrease all pen width in selected state
            self.pen.setWidth(self.pen.width() - 2)
            self.hoverPen.setWidth(self.hoverPen.width() - 2)
            self.handlePen.setWidth(self.handlePen.width() - 2)
        # Force redraw to reflect selected status
        self.update()

    def getMenu(self):
        """
        Generates Annotation ROI menu with custom actions for just the ROI
        :return: Menu
        """
        self.menu = QtWidgets.QMenu()
        self.menu.setTitle(f"Annotation Menu")
        remove_action = QtGui.QAction("Remove annotation", self.menu)
        export_action = QtGui.QAction("Export annotation", self.menu)
        # Emit remove request when triggered from context menu
        remove_action.triggered.connect(self.remove_roi)
        export_action.triggered.connect(self.export_roi)

        self.menu.addActions([remove_action, export_action])
        self.menu.addSeparator()
        return self.menu

    def get_tooltip(self):
        """
        Build tool tip rich text string using current annotation state
        :return: Annotation tooltip str
        """
        return f"""
            <table style=\"font-family: monospace\">
            <tr>
                <td style="padding-right:10px">Start</td>
                <td>[</td>
                <td align=right>{self.annotation.start:.02f}</td>
                <td>,</td>
                <td  align=right>{self.annotation.length:.02f}</td>
                <td>]</td>
                <td>s</td>
            </tr>
            <tr>
                <td style="padding-right:10px">Freq.</td>
                <td>[</td>
                <td align=right>{self.annotation.low:.02f}</td>
                <td>,</td>
                <td align=right>{self.annotation.high:.02f}</td>
                <td>]</td>
                <td>Hz</td>
            </tr>
             <tr>
                <td style="padding-right:10px">Group</td>
                <td colspan="6">
                    {self.annotation.group if self.annotation.group else "Empty"}
                </td>
            </tr>
            <tr>
                <td style="padding-right:10px">Label</td>
                <td colspan="6">
                    {self.annotation.label if self.annotation.label else "Empty"}
                </td>
            </tr>
            </table>
        """
