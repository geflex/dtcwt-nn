import pytest

from helpers.serialization import model_to_dict
from widgets.dtcwt import DTCWT, DtcwtModel
from widgets.fourier import FourierModel, Fourier
from widgets.gui_settings import GuiModel, GUIConfig
from widgets.model_info import ModelConfig, ModelConfigModel
from widgets.runner import RunnerConfig, RunnerModel

PROJECT_MODELS = (
    RunnerConfig, ModelConfig, GUIConfig, Fourier, DTCWT,
    RunnerModel, ModelConfigModel, GuiModel, FourierModel, DtcwtModel
)


@pytest.mark.parametrize('model_cls', PROJECT_MODELS)
def test_project_model_to_dict(model_cls):
    assert model_to_dict(model_cls())
