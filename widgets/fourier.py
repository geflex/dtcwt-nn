import numpy as np
import features
from pyqt_framework.storage import Storage
from pyqt_framework.model import Field
from widgets.feature import Feature, FixedFragmentFeature


class Fourier(Storage, Feature):
    fragment_len: int = 1024
    fs: int = 20_000

    def __post_init__(self):
        super().__init__()

    @property
    def feature_size(self) -> int:
        return features.fourier_shape(self.fragment_len)

    def __call__(self, sample):
        return features.fourier(sample, 1 / self.fs)


class FourierModel(FixedFragmentFeature):
    fs: int = Field(verbose_name='Fs', default=Fourier.fs)

    @property
    def feature_size(self) -> int:
        return features.fourier_shape(self.fragment_len)

    def __call__(self, sample: np.array):
        return features.fourier(sample, 1 / self.fs)
