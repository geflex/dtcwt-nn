import keras
from PyQt6.QtCore import QT_TR_NOOP, QObject, pyqtSignal

from pyqt_framework.model import Model, Field
from pyqt_framework.widgets.simple import FloatSpinFactory, IntSpinFactory
from pyqt_framework.widgets.path import PathEditFactory
from pyqt_framework.widgets.model_editor import ModelSelectorFactory
from widgets.adam import AdamParams
from widgets.feature import Feature


def get_feature_names():
    return [f.__class__.__name__ for f in Feature.__subclasses__()]


class FitModel(Model):
    model_path = Field(PathEditFactory(QT_TR_NOOP('Загрузить модель')))
    from_path = Field(PathEditFactory(QT_TR_NOOP('Выбрать директорию')), default='dir/features.numpy',
                      verbose_name=QT_TR_NOOP('Путь к характеристикам'))
    batch_size = Field(IntSpinFactory(), default=32)
    train_test_ratio = Field(FloatSpinFactory(val_range=(0, 1), step=0.1), default=0.8)
    epochs_count = Field(IntSpinFactory(), default=50)
    optimizer: AdamParams = Field(ModelSelectorFactory())


class GUICallback(keras.callbacks.Callback):
    pass


class FitWorker(QObject):
    train_result = pyqtSignal(float, float)
    validation_result = pyqtSignal(float, float)

    def __init__(self, fit_model: FitModel) -> None:
        super().__init__()
        self._fit_model = fit_model

    def run(self):
        pass
