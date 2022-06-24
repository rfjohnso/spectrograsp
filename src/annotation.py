from enum import Enum
from PySide6 import QtCore
from dataclasses import dataclass


class AnnotationSource(Enum):
    FILE = 1
    USER = 2
    AUTOMATIC = 3


class Annotation(QtCore.QObject):

    annotation_changed = QtCore.Signal(object)
    annotation_selected = QtCore.Signal(object)
    annotation_hovered = QtCore.Signal(object)

    def __init__(self,
                 annotation_id: int = None,
                 source: AnnotationSource = None,
                 label: str = None,
                 group: str = None,
                 **kwargs):

        super(Annotation, self).__init__()
        # Annotation ID
        self.id = annotation_id
        # Annotation group ID
        self.group = group or None
        self.label = label or None
        # Annotation source
        self.source = source
        # Starting time in seconds
        self.start = kwargs.get('start', 0)
        # Duration time in seconds
        self.length = kwargs.get('length', 1)
        # Higher frequency
        self.high = kwargs.get('high', None)
        # Lowest frequency
        self.low = kwargs.get('low', None)
        # Metadata dictionary
        self.metadata = kwargs
        # List of labels
        self.labels = []

        self.selected = False

    @property
    def author(self):
        return self.metadata.get('author', None)

    @property
    def comment(self):
        return self.metadata.get('comment', None)

    @property
    def symbol_rate(self):
        return self.metadata.get('symbol_rate', None)

    @property
    def confidence(self):
        return self.metadata.get('confidence', None)

    @author.setter
    def author(self, author):
        self.metadata['author'] = author

    @comment.setter
    def comment(self, comment):
        self.metadata['comment'] = comment

    @symbol_rate.setter
    def symbol_rate(self, symbol_rate):
        self.metada['symbol_rate'] = symbol_rate

    @confidence.setter
    def confidence(self, confidence):
        self.metadata['confidence'] = confidence

    def add_field(self, key, value):
        self.metadata[key] = value
        self.annotation_changed.emit(self)

    @classmethod
    def merge_annotations(cls, annotations: list):

        start = min(a.start for a in annotations)
        end = max(a.start + a.length for a in annotations)
        low = min(a.low for a in annotations)
        high = max(a.high for a in annotations)

        # Use annotations labels and groups if they are all the same
        label = annotations[0].label if all(a.label == annotations[0].label for a in annotations) else None
        group = annotations[0].group if all(a.group == annotations[0].group for a in annotations) else None

        new_annotation = cls(source=AnnotationSource.USER,
                             start=start,
                             length=end-start,
                             low=low,
                             high=high,
                             label=label,
                             group=group)

        return new_annotation

    def to_dict(self):
        return {
            "start": self.start,
            "length": self.length,
            "low": self.low,
            "high": self.high,
            "author": self.author,
            "comment": self.comment,
            "symbol_rate": self.metadata.get("symbol_rate", ""),
            "label": self.label,
            "confidence": self.confidence,
            "group": self.group
        }