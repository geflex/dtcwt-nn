from typing import Iterable, Sequence
import numpy as np
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

from helpers.pyqt.translate import QBaseWidget


class ClassProbabilitiesWidget(QBaseWidget):
    def __init__(self, parent=None, flags=Qt.WindowType.Widget):
        super().__init__(parent, flags)
        self._last_dominant_class = 0

        self.names_layout = QVBoxLayout()
        self.probabilities_layout = QVBoxLayout()

        self.h_layout = QHBoxLayout(self)
        self.h_layout.setContentsMargins(6, 0, 6, 0)
        self.h_layout.addLayout(self.names_layout)
        self.h_layout.addLayout(self.probabilities_layout)

    def reset_probabilities(self):
        for i in range(self.probabilities_layout.count()):
            self.probabilities_layout.itemAt(i).widget().setText('0')  # noqa

    @property
    def classes_count(self):
        return self.probabilities_layout.count()

    @classes_count.setter
    def classes_count(self, n: int):
        self.reset_probabilities()
        curr_len = self.classes_count
        if n > curr_len:
            for i in range(curr_len, n):
                self.names_layout.addWidget(QLabel(str(i)))
                self.probabilities_layout.addWidget(QLabel('0'))
                self._last_dominant_class = 0
        if n < curr_len:
            for i in range(curr_len-1, n-1, -1):
                # noinspection PyTypeChecker
                self.names_layout.itemAt(i).widget().setParent(None)
                # noinspection PyTypeChecker
                self.probabilities_layout.itemAt(i).widget().setParent(None)

    def update_classnames(self, classnames: Sequence[str]):
        for i in range(min(len(classnames), self.names_layout.count())):
            # noinspection PyUnresolvedReferences
            self.names_layout.itemAt(i).widget().setText(classnames[i])

    def update_classname_at(self, i: int, newname: str):
        # noinspection PyUnresolvedReferences
        self.names_layout.itemAt(i).widget().setText(newname)

    def update_probabilities(self, probabilities: Iterable[float]):
        dominant_class = np.argmax(probabilities)
        for i, prob in enumerate(probabilities, start=0):
            cls_name_label = self.names_layout.itemAt(i).widget()
            prob_label = self.probabilities_layout.itemAt(i).widget()

            # noinspection PyUnresolvedReferences
            prob_label.setText(f'{prob:.2f}')
            if i == dominant_class:
                cls_name_label.setStyleSheet('font-weight: bold;')
                prob_label.setStyleSheet('font-weight: bold;')
            elif i == self._last_dominant_class:
                cls_name_label.setStyleSheet('font-weight: normal;')
                prob_label.setStyleSheet('font-weight: normal;')
        self._last_dominant_class = dominant_class
