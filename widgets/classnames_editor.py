from typing import Iterable

import widgets.runner as data_models
from pyqt_framework.storage import connect_output
from PyQt6 import QtGui, QtWidgets


class ClassnamesEditor(QtWidgets.QPlainTextEdit):
    def __init__(self, model_config: data_models.ModelConfig):
        super().__init__()
        self.model_config = model_config
        connect_output(model_config, 'classnames', lambda v: setattr(self, 'data', v))
        self.textChanged.connect(self.on_text_changed)

    @property
    def data(self) -> list[str]:
        return self.toPlainText().split('\n')

    @data.setter
    def data(self, classnames: Iterable[str]):
        text = '\n'.join(classnames)
        # if text == self.toPlainText():
        #     return
        newpos = min(len(text), self.textCursor().position())
        self.setPlainText(text)  # this moves cursor to position 0
        cursor = QtGui.QTextCursor(self.textCursor())
        cursor.setPosition(newpos)
        self.setTextCursor(cursor)

    def on_text_changed(self):
        self.model_config.set_field_value('classnames', self.data)
