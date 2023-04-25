import dataclasses
import json
import logging
import warnings
from dataclasses import fields, is_dataclass
from typing import Sequence, Any, Type, Callable

from PyQt6.QtWidgets import QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit, QWidget
from PyQt6.QtCore import QObject, pyqtSignal

from helpers.serialization import init_model_from_dict, model_to_dict
from pyqt_framework.model import AbstractModel, FieldT, field_name

_ANY_CHANGED = 'any_changed'


class Storage(AbstractModel):
    def __init_subclass__(cls, *args, **kwargs):
        # noinspection PyMethodFirstArgAssignment
        cls = dataclasses.dataclass(cls)
        pyqt_storage(cls)

    def as_dict(self, dict_factory=dict):
        return dataclasses.asdict(self, dict_factory=dict_factory)  # noqa

    def from_dict(self, data: dict):
        return init_model_from_dict(self.__class__, data)

    def __post_init__(self, *args, **kwargs):
        super().__init__()

    @classmethod
    def fields(cls):
        # noinspection PyDataclass
        return dataclasses.fields(cls)

    def any_changed_emit(self, field: FieldT, value: Any):
        fieldname = field_name(field)
        if hasattr(self, _ANY_CHANGED):
            getattr(self, _ANY_CHANGED).emit(fieldname, value)

    def any_changed_connect(self, callback: Callable[[str, Any], None]):
        if hasattr(self, _ANY_CHANGED):
            getattr(self, _ANY_CHANGED).connect(callback)

    def changed_emit(self, field: FieldT, value: Any):
        fieldname = field_name(field)
        if hasattr(self, f'{fieldname}_changed'):
            getattr(self, f'{fieldname}_changed').emit(value)

    def changed_connect(self, field: FieldT, callback: Callable[[Any], None]):
        fieldname = field_name(field)
        if hasattr(self, f'{fieldname}_changed'):
            getattr(self, f'{fieldname}_changed').connect(callback)

    def get_field_value(self, field: FieldT):
        attrname = field_name(field)
        return getattr(self, attrname)

    def set_field_value(self, attrname: str, v: Any):
        if getattr(self, attrname, None) == v:
            return
        if is_dataclass(v) and hasattr(self, attrname):
            obj_to_update = getattr(self, attrname)
            for field in fields(obj_to_update):
                new_value = getattr(v, field.name)
                obj_to_update.set_field_value(field.name, new_value)

        else:
            setattr(self, attrname, v)

        logging.debug(f'{self}.{attrname} set to {v}')

        self.changed_emit(attrname, v)
        self.any_changed_emit(attrname, v)


def pyqt_storage(cls: Type[Storage], exclude: Sequence[str] = ()):
    """create signal for each field of the QObject dataclass"""
    if not issubclass(cls, QObject):
        warnings.warn(f'{cls} is not a subclass of QObject')
    if '__post_init__' not in cls.__dict__:
        warnings.warn(f'{cls} has no __post_init__')

    for field in cls.fields():
        attrname = field_name(field)
        if not hasattr(cls, f'{attrname}_changed') and attrname not in exclude:
            setattr(cls, f'{attrname}_changed', pyqtSignal(object))
    setattr(cls, _ANY_CHANGED, pyqtSignal(str, object))

    return cls


def connect_json_file(storage: AbstractModel, filename: str):
    def save_json(attrname, val):
        logging.info(f'{filename} saved')
        d = model_to_dict(storage)
        with open(filename, 'w') as f:
            json.dump(d, f)
    storage.any_changed_connect(save_json)


# TODO: add other classes
slots_signals = {
    QCheckBox: (QCheckBox.setChecked, 'clicked'),
    QSpinBox: (QSpinBox.setValue, 'valueChanged'),
    QDoubleSpinBox: (QDoubleSpinBox.setValue, 'valueChanged'),
    QComboBox: (QComboBox.setCurrentText, 'currentTextChanged'),
    QLineEdit: (QLineEdit.setText, 'textChanged')
}


def get_slot_signal(inp):
    for k, v in slots_signals.items():
        if isinstance(inp, k):
            return v
    raise KeyError(inp.__class__)


def connect_output(storage: AbstractModel, varname: str, output_setter: Callable[[Any], None]):
    """
    1. call setter now;
    2. connect it to varname_changed.
    """
    output_setter(getattr(storage, varname))
    storage.changed_connect(varname, output_setter)


def connect_input(inp: QWidget, storage: AbstractModel, varname: str):
    """
    1. call input setter now;
    2. connect it to storage.varname_changed`;
    3. connect storage.set_varname to input.value_changed.
    """
    def var_setter(v):
        storage.changed_emit(varname, v)
    inp_setter, inp_changed_sig = get_slot_signal(inp)

    inp_setter(inp, storage.get_field_value(varname))  # 1.
    storage.changed_connect(varname, lambda v: inp_setter(inp, v))  # 2.
    getattr(inp, inp_changed_sig).connect(var_setter)  # 3.
    return var_setter, inp_setter
