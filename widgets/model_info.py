from dataclasses import dataclass

import keras
from helpers.pyqt import MONOSPACE_FONT
from pyqt_framework.model import Model, Field
from pyqt_framework.widgets.model_editor import ModelSelectorFactory
from pyqt_framework.widgets.list_text_editor import ListTextEditorFactory
from pyqt_framework.storage import Storage
from PyQt6 import QtGui
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QMessageBox

from widgets.dtcwt import DTCWT
from widgets.feature import Feature, FixedFragmentFeature


class ModelConfig(Storage):
    feature: Feature = DTCWT
    classnames: list[str]
    fs: int

    def __post_init__(self):
        super().__init__()

    def validate(self) -> list[str]:
        return self.feature.validate()


class ModelConfigModel(Model):
    feature: FixedFragmentFeature = Field(ModelSelectorFactory())
    classnames = Field(ListTextEditorFactory())


def model_info_message(parent: QObject, model: keras.models.Model, model_path: str):
    message_box = QMessageBox(parent)
    message_box.setFont(QtGui.QFont(MONOSPACE_FONT))
    lines = [f'Path: {model_path}']
    model.summary(print_fn=lines.append)
    message_box.setText('\n'.join(lines))
    return message_box
