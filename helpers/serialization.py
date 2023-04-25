import json
from dataclasses import _MISSING_TYPE  # noqa
from os import PathLike
from typing import Type, Iterable, Union

from pyqt_framework.compat import get_field_type
from pyqt_framework.model import AbstractModel, is_model


def init_model_from_dict(cls: Type[AbstractModel], data: dict):
    kwargs = {}
    for field in cls.fields():
        fieldname = field.name
        t = get_field_type(cls, field)
        if fieldname in data:
            val = data[fieldname]
        elif field.default != _MISSING_TYPE:
            val = field.default
        else:
            raise KeyError(fieldname)

        if is_model(t):
            if '_type_' in val:
                subclass_name = val['_type_']
                t = [c for c in t.__subclasses__() if c.__name__.lower() == subclass_name.lower()][
                    0]  # type: Type[AbstractModel]
            kwargs[fieldname] = init_model_from_dict(t, val)
        else:
            kwargs[fieldname] = val
    return cls(**kwargs)  # noqa


_SERIALIZE_EXCLUDE = '_serialize_exclude'


def set_serialize_exclude(exclude: Iterable[str]):
    def decorator(cls):
        setattr(cls, _SERIALIZE_EXCLUDE, exclude)
        return cls
    return decorator


PathT = Union[PathLike, str]


def model_to_dict(obj: AbstractModel):
    def dict_factory(*args, **kwargs):
        kwargs = dict(*args, **kwargs)
        return {k: v for k, v in kwargs.items() if k not in getattr(obj, _SERIALIZE_EXCLUDE, ())}
    return obj.as_dict(dict_factory)


def model_json_deserialize(cls: Type[AbstractModel], path: PathT):
    with open(path, 'r') as f:
        d = json.load(f)
    return init_model_from_dict(cls, d)
