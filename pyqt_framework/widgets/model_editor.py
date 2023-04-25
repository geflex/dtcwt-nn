from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Type, Any, Callable, Union

from PyQt6.QtWidgets import QWidget, QComboBox, QHBoxLayout, QFormLayout, QVBoxLayout, QLabel, \
    QCheckBox, QDoubleSpinBox, QSpinBox, QLineEdit

from helpers.pyqt.translate import QTransLabel, QBaseWidget
from pyqt_framework.model import WidgetFactory, Model, Field, LayoutClassT, AbstractModel
from pyqt_framework.widgets.list_text_editor import ListTextEditorFactory, ListTextEditor
from pyqt_framework.widgets.simple import IntSpinFactory, FloatSpinFactory, \
    CheckBoxFactory, LineEditFactory, ComboFactory
from pyqt_framework.widgets.path import PathEditFactory, PathEdit


def _subclass_names(cls):
    return [subcls.__name__ for subcls in cls.__subclasses__()]


class ModelEditorFactory(WidgetFactory):
    """
    Create widget representing a model with connected inputs and outputs
    """
    def __call__(self, model: Model, field: Field) -> QWidget:
        widget = QWidget()
        inner_model = model.get_field_value(field)
        layout = create_form_layout(inner_model)
        widget.setLayout(layout)
        return widget


class ModelSelectorFactory(WidgetFactory):
    """
    Widget that allows you to select and edit concrete subtype of the field type
    """
    def __call__(self, model: Model, field: Field) -> QWidget:
        names = _subclass_names(field.value_type)
        combo = QComboBox()
        combo.addItems(names)

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(combo)
        inner_model = model.get_field_value(field)  # type: Model
        model_layout = create_layout(inner_model)
        layout.addLayout(model_layout)

        return widget


def get_widget_factory(datatype):
    if datatype.__subclasses__():
        return ModelSelectorFactory()
    else:
        return ModelEditorFactory()


@dataclass
class FieldDefaults:
    widget_type: Type[QWidget]
    get_widget_factory: Union[Type[WidgetFactory], Callable[[Any], Type[WidgetFactory]]]


DEFAULTS = {
    bool: FieldDefaults(QCheckBox, CheckBoxFactory()),
    int: FieldDefaults(QSpinBox, IntSpinFactory()),
    float: FieldDefaults(QDoubleSpinBox, FloatSpinFactory()),
    str: FieldDefaults(QLineEdit, LineEditFactory()),
    list[str]: FieldDefaults(ListTextEditor, ListTextEditorFactory()),
    Enum: FieldDefaults(QComboBox, lambda e: ComboFactory([m.value for m in e])),
    Model: FieldDefaults(QWidget, ModelEditorFactory()),
    Path: FieldDefaults(PathEdit, PathEditFactory()),
}


def get_default_factory(datatype: Any) -> WidgetFactory:
    for dtype, defaults in DEFAULTS.items():
        if issubclass(datatype, dtype):
            get_factory = defaults.get_widget_factory
            if isinstance(get_factory, WidgetFactory):
                return get_factory
            else:
                return get_factory(datatype)
    raise KeyError(f'No defaults is registered for type {datatype}')


def create_form_layout(model: AbstractModel, QLabelCls=QTransLabel) -> QFormLayout:
    """vertical form layout"""
    layout = QFormLayout()
    for field in model.fields():
        label = QLabelCls(field.verbose_name)
        field_widget = create_field_widget(field, model)
        layout.addRow(label, field_widget)
    return layout


def create_layout(model: AbstractModel,
                  LayoutClass: LayoutClassT = QVBoxLayout,
                  LayoutClass2: LayoutClassT = QHBoxLayout,
                  QLabelCls: Type[QLabel] = QTransLabel):
    layout = LayoutClass()
    for field in model.fields():
        label = QLabelCls(field.name)
        field_widget = create_field_widget(field, model)

        line = LayoutClass2()
        line.addWidget(label)
        line.addWidget(field_widget)

        layout.addLayout(line)
    return layout


def create_model_widget(model: AbstractModel, QWidgetCls=QBaseWidget) -> QBaseWidget:
    widget = QWidgetCls()
    layout = create_layout(model)
    widget.setLayout(layout)
    return widget


def create_field_widget(field: Field, model: Model) -> QWidget:
    if field.widget_factory is not None:
        return field.widget_factory(model, field)
    widget_factory = get_default_factory(field.value_type)
    return widget_factory(model, field)
