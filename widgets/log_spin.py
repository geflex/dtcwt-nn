import numpy as np
from PyQt6.QtWidgets import QSpinBox
from PyQt6 import QtGui


class QLogSpinBox(QSpinBox):
    def stepBy(self, steps: int) -> None:
        if steps == 1:
            new_value = self.value() * 2
        elif steps == -1:
            new_value = self.value() // 2
        else:
            return super().stepBy(steps)
        if new_value < self.minimum() or new_value > self.maximum():
            return
        self.setValue(new_value)

    def validate(self, inp: str, pos: int):
        invalid = QtGui.QValidator.State.Invalid, str(self.value()), pos
        try:
            int_inp = int(inp)
        except ValueError:
            return invalid
        if int_inp < self.minimum() or int_inp > self.maximum():
            return invalid
        if np.log2(int_inp) % 1 != 0:
            return invalid
        return super().validate(inp, pos)
