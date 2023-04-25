import dataclasses
from dataclasses import Field as DataclassField
from typing import Union

from pyqt_framework.model import Model, Field


def as_dict(obj):
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    elif isinstance(obj, Model):
        return obj.as_dict()
    else:
        raise TypeError('obj must be a dataclass or Model instance')


def fields(obj):
    try:
        dataclasses.fields(obj)
    except TypeError:
        return obj.__fields__


def get_field_type(cls, field: Union[Field, DataclassField]):
    if isinstance(field, Field):
        return field.value_type
    return cls.__annotations__[field.name]
