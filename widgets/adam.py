from abc import abstractmethod

from pyqt_framework.model import Model, Field
from pyqt_framework.widgets.simple import FloatSpinFactory
from keras.optimizers import adam_v2


class ArgModel(Model):
    @abstractmethod
    def __call__(self):
        return


class AdamParams(ArgModel):
    learning_rate: float = Field(default=0.001)
    beta_1: float = Field(default=0.9)
    beta_2: float = Field(default=0.999)
    epsilon: float = Field(default=1e-7)
    amsgrad: bool = Field(default=False)

    def __call__(self):
        return adam_v2.Adam(**self.as_dict())
