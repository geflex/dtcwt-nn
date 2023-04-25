from pathlib import Path

from PyQt6.QtCore import QT_TR_NOOP

from pyqt_framework.model import Model, Field
from pyqt_framework.widgets.path import PathEditFactory, OpenFilenamesFactory
from pyqt_framework.widgets.model_editor import ModelSelectorFactory
from widgets.dtcwt import DtcwtModel
from widgets.feature import Feature


class ExtractorModel(Model):
    filenames: list[Path] = Field(OpenFilenamesFactory(QT_TR_NOOP('Open wav files')), default=())
    to_path: Path = Field(PathEditFactory(QT_TR_NOOP('Open feature file')), default='dir/features.numpy')
    feature: Feature = Field(ModelSelectorFactory(), default=DtcwtModel)
