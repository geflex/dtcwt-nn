from abc import abstractmethod, ABC

import numpy as np
from PyQt6.QtCore import QT_TR_NOOP

from pyqt_framework.model import Model, Field


class Feature:
    fragment_len: int
    feature_size: tuple[int, int]

    @abstractmethod
    def __call__(self, sample: np.array) -> np.array:
        pass

    def validate(self) -> list[str]:
        return []


class FixedFragmentFeature(Model, Feature, ABC):
    fragment_len: int = Field(verbose_name=QT_TR_NOOP('Длина фрагмента'), default=1024)
