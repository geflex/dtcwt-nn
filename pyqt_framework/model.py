from __future__ import annotations

import copy
import dataclasses
from abc import abstractmethod
from typing import Any, Type, Union, Callable, Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout


class Field:
    """
    Descriptor class for working with serializable and notifying attributes.

    if serialization_name is None it will be automatically set
    default has MISSING value because it can be of any type includint None
    """

    @property
    def name(self):
        """Added for compatibility with dataclass fields"""
        return self.serialization_name

    def __init__(self, widget_factory: WidgetFactory = None,
                 serialization_name: str = None,
                 verbose_name: str = None,
                 default: Any = dataclasses.MISSING, value_type: type = None):
        if widget_factory is not None:
            self.widget_factory = widget_factory
        self.serialization_name = serialization_name
        self.verbose_name = verbose_name or serialization_name
        self.default = default
        self.value_type = value_type

    def copy(self, **kwargs):
        # NOT FOR USER INPUT
        new = copy.deepcopy(self)
        new.__dict__.update(**kwargs)

    def has_default(self):
        return hasattr(self, 'default')

    def maybe_init_model_class(self, cls: Type[Model]) -> Type[Model]:
        # i don't wanna to create a metaclass, so all initializations are implemented here.
        # Note: if superclass __fields__ will be changed it will not affect on the subclasses
        if '__fields__' not in cls.__dict__:
            if hasattr(cls, '__fields__'):  # if superclass has __fields__
                # this makes a copy of superclass.__fields__ in this (initializing) class.__dict__
                cls.__fields__ = cls.__fields__.copy()
            else:
                cls.__fields__ = {}
        return cls

    def __set_name__(self, model_cls: Type[Model], name: str):
        """
        initialize field from its attribute name in model class
        """
        self.maybe_init_model_class(model_cls)
        model_cls.__fields__[name] = self

        if self.value_type is None:
            self.value_type = model_cls.__annotations__.get(name)
        if self.serialization_name is None:
            self.serialization_name = name
        if self.verbose_name is None:
            self.verbose_name = name

    def __get__(self, obj: Optional[Model], model_cls: Type[Model]):
        if obj is None:
            return self
        return obj.get_field_value(self.serialization_name)

    def __set__(self, obj: Model, value: Any):
        obj.set_field_value(self.serialization_name, value)

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.serialization_name}")'


FieldT = Union[str, Field]

def field_name(field: FieldT) -> str:
    if isinstance(field, Field):
        field = field.name
    return field


class AbstractModel:
    @classmethod
    @abstractmethod
    def fields(cls) -> list[Field]:
        pass

    @abstractmethod
    def as_dict(self, dict_factory=dict) -> dict:
        pass

    @abstractmethod
    def from_dict(self, data: dict):
        """insert values from `data` to self"""
        pass

    @abstractmethod
    def any_changed_connect(self, callback: Callable[[str, Any], None]):
        pass

    @abstractmethod
    def changed_connect(self, field: FieldT, callback: Callable[[Any], None]):
        """will be emited when field value changes"""

    @abstractmethod
    def any_changed_emit(self, field: FieldT, value: Any):
        pass

    @abstractmethod
    def changed_emit(self, field: FieldT, value: Any):
        """sends the signal notifying that the `field` value of `self` was changed to `value`"""

    @abstractmethod
    def set_field_value(self, field_n: FieldT, value: Any):
        """set new value for field and notifies all value_changed subscribers"""

    @abstractmethod
    def get_field_value(self, field: FieldT):
        pass


def is_model(obj):
    return dataclasses.is_dataclass(obj) or isinstance(obj, Model)


LayoutClassT = Union[Type[QHBoxLayout], Type[QVBoxLayout]]


class Model(AbstractModel):
    __fields__: dict[str, Field]  # initialized in Field.__set_name__
    __data__: dict[str, Any]
    __changed_callbacks__: dict[str, list[Callable[[Any], None]]]
    __any_changed_callbacks__: list[Callable[[str, Any], None]]

    @classmethod
    def fields(cls):
        return list(cls.__fields__.values())

    def as_dict(self, dict_factory=dict):
        # out = {}
        # for field in self.__fields__.values():
        #     out[field.serialization_name] = field.__get__(self, self.__class__)
        # return out
        return dict_factory(**self.__dict__)

    def from_dict(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)

    def any_changed_connect(self, callback: Callable[[str, Any], None]):
        self.__any_changed_callbacks__.append(callback)

    def changed_connect(self, field: FieldT, callback: Callable[[Any], None]):
        """will be emited when field value changes"""
        field_n = field_name(field)
        if field_n not in self.__changed_callbacks__:
            self.__changed_callbacks__[field_n] = []
        self.__changed_callbacks__[field_n].append(callback)

    def any_changed_emit(self, field: FieldT, value: Any):
        field_n = field_name(field)
        for cb in self.__any_changed_callbacks__:
            cb(field_n, value)

    def changed_emit(self, field: FieldT, value: Any):
        """sends the signal notifying that the `field` value of `self` was changed to `value`"""
        field_n = field_name(field)
        if field_n in self.__changed_callbacks__:
            for cb in self.__changed_callbacks__[field_n]:
                cb(value)
        self.any_changed_emit(field, value)

    def set_field_value(self, field_n: FieldT, value: Any):
        """set new value for field and notifies all value_changed subscribers"""
        field_n = field_name(field_n)
        self.__data__[field_n] = value
        self.changed_emit(field_n, value)

    def get_field_value(self, field: FieldT):
        field = field_name(field)
        return self.__data__[field]

    def __init__(self, **kwargs):
        self.__data__ = {}
        for field in self.__fields__.values():
            field_n = field_name(field)
            if field.has_default():
                value = kwargs.get(field_n, field.default)
            else:
                value = kwargs[field_n]
            self.__data__[field_n] = value
        self.__changed_callbacks__ = {}

    def __len__(self):
        return len(self.__data__)


WidgetFactory = Callable[[Model, Field], QWidget]


def connect_output(storage: Model, field: Field, output_setter: callable):
    """
    1. call setter now;
    2. connect it to varname_changed.
    """
    pass  # TODO


def connect_input(inp, storage, field: Field):
    """
    1. call input setter now;
    2. connect it to storage.varname_changed`;
    3. connect storage.set_varname to input.value_changed.
    """
    pass  # TODO
