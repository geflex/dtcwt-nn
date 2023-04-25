from typing import Iterable

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import pyqtSignal

from pyqt_framework.widgets.simple import SimpleWidgetFactory


class ListTextEditor(QtWidgets.QPlainTextEdit):
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


class ListTextEditorFactory(SimpleWidgetFactory):
    WidgetType = ListTextEditor
    DataType = list

    def widget_value_changed(self, widget: WidgetType) -> pyqtSignal:
        return widget.textChanged  # noqa

    def set_widget_value(self, widget: WidgetType, value: DataType):
        widget.data = value
