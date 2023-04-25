from abc import abstractmethod
from functools import partial
from typing import Any, Iterable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDoubleSpinBox, QSpinBox, QComboBox, QCheckBox, QLineEdit

from helpers.pyqt.translate import QBaseWidget
from pyqt_framework.model import WidgetFactory, Model, Field


class SimpleWidgetFactory(WidgetFactory):
    WidgetType = QBaseWidget
    DataType = Any

    def __init__(self, *, WidgetType=None, DataType=None):
        if WidgetType is not None:
            self.WidgetType = WidgetType
        if DataType is not None:
            self.DataType = DataType

    def create_widget(self) -> WidgetType:
        return self.WidgetType()

    @abstractmethod
    def set_widget_value(self, widget: WidgetType, value: DataType):
        pass

    @abstractmethod
    def widget_value_changed(self, widget: WidgetType) -> pyqtSignal:
        pass

    def __call__(self, model: Model, field: Field) -> WidgetType:
        widget = self.create_widget()
        value = model.get_field_value(field)
        self.set_widget_value(widget, value)
        self.widget_value_changed(widget).connect(partial(field.__set__, model))
        model.changed_connect(field, lambda v: self.set_widget_value(widget, v))
        return widget


class FloatSpinFactory(SimpleWidgetFactory):
    WidgetType = QDoubleSpinBox
    DataType = float

    def __init__(self, val_range: tuple[DataType, DataType] = None, step: DataType = 1, **kwargs):
        super(FloatSpinFactory, self).__init__(**kwargs)
        self.val_range = val_range
        self.step = step

    def create_widget(self):
        widget = self.WidgetType()
        if self.val_range is not None:
            widget.setRange(*self.val_range)
        widget.setSingleStep(self.step)
        return widget

    def set_widget_value(self, widget: WidgetType, value: DataType):
        widget.setValue(value)

    def widget_value_changed(self, widget: WidgetType):
        return widget.valueChanged


class IntSpinFactory(FloatSpinFactory):
    WidgetType = QSpinBox
    DataType = int


class ComboFactory(SimpleWidgetFactory):
    WidgetType = QComboBox
    DataType = str

    def __init__(self, values: Iterable[str] = (), **kwargs):
        super(ComboFactory, self).__init__(**kwargs)
        self.values = values

    def create_widget(self) -> WidgetType:
        widget = self.WidgetType()
        widget.addItems(self.values)
        return widget

    def set_widget_value(self, widget: WidgetType, value: DataType):
        widget.setCurrentText(value)

    def widget_value_changed(self, widget: WidgetType) -> pyqtSignal:
        return widget.currentTextChanged  # noqa, this is signal


class CheckBoxFactory(SimpleWidgetFactory):
    WidgetType = QCheckBox
    DataType = bool

    def set_widget_value(self, widget: WidgetType, value: DataType):
        widget.setChecked(value)

    def widget_value_changed(self, widget: WidgetType) -> pyqtSignal:
        return widget.stateChanged  # noqa, this is signal


class LineEditFactory(SimpleWidgetFactory):
    WidgetType = QLineEdit
    DataType = str

    def set_widget_value(self, widget: WidgetType, value: DataType):
        widget.setText(value)

    def widget_value_changed(self, widget: WidgetType) -> pyqtSignal:
        return widget.textChanged  # noqa, this is
