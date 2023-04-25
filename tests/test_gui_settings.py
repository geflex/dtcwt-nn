import pytest
from widgets.gui_settings import *


BUPU = 'BuPu'
EN = 'en'


class TestGUIConfig:
    def test_init_no_args(self):
        config = GUIConfig()
        assert config.colormap == GUIConfig.colormap
        assert config.locale == GUIConfig.locale

    def test_init(self):
        config = GUIConfig(BUPU, EN)
        assert config.colormap == BUPU
        assert config.locale == EN


class TestGuiModel:
    def test_init_no_args(self):
        model = GuiModel()
        assert model.colormap == GUIConfig.colormap
        assert model.locale == GUIConfig.locale

    def test_init_kwargs(self):
        model = GuiModel(colormap=BUPU, locale=EN)
        assert model.colormap == BUPU
        assert model.locale == EN


class TestGuiWidget:
    def test_init(self, qtbot):
        model = GuiModel()
        widget = GUISettingsWidget(model)
