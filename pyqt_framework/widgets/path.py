from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QFileDialog

from helpers.pyqt.translate import QBaseWidget
from pyqt_framework.widgets.simple import LineEditFactory, SimpleWidgetFactory


class PathEdit(QBaseWidget):
    def __init__(self, button_text: str):
        super(PathEdit, self).__init__()
        self.line_edit = QLineEdit()
        self.button = QPushButton(button_text)
        layout = QHBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)
        self.setLayout(layout)


class PathEditFactory(LineEditFactory):
    WidgetType = PathEdit
    DataType = str

    def __init__(self, button_text: str = "Open", **kwargs):
        super(PathEditFactory, self).__init__(**kwargs)
        self.button_text = button_text

    def create_widget(self) -> WidgetType:
        return self.WidgetType(self.button_text)

    def set_widget_value(self, widget: WidgetType, value: DataType):
        widget.line_edit.setText(value)

    def widget_value_changed(self, widget: WidgetType) -> pyqtSignal:
        return widget.line_edit.textChanged  # noqa


class OpenFilenamesWidget(QBaseWidget):
    value_changed = pyqtSignal(list)

    def __init__(self, button_text: str = "Open files", caption: str = "Open files", filt: str = '*'):
        super(OpenFilenamesWidget, self).__init__()
        self.caption = caption
        self.filter = filt
        self.button = QPushButton(button_text)
        self.button.clicked.connect(self.open_files)

    def open_files(self):
        filenames, filt = QFileDialog.getOpenFileNames(
            self, caption=self.caption, filter=self.filter,
        )
        self.value_changed.emit(filenames)


class OpenFilenamesFactory(SimpleWidgetFactory):
    WidgetType = OpenFilenamesWidget
    DataType = list

    def __init__(self, button_text: str = "Open files", **kwargs):
        super(OpenFilenamesFactory, self).__init__(**kwargs)
        self.button_text = button_text

    def widget_value_changed(self, widget: WidgetType) -> pyqtSignal:
        return widget.value_changed

    def set_widget_value(self, widget: WidgetType, value: DataType):
        pass

    def create_widget(self) -> WidgetType:
        return OpenFilenamesWidget(self.button_text)
