from pathlib import Path

import matplotlib.pyplot as plt
from PyQt6.QtCore import QT_TR_NOOP

from helpers.pyqt import find_locales
from pyqt_framework.model import Model, Field
from pyqt_framework.storage import Storage
from pyqt_framework.widgets.model_editor import create_model_widget
from pyqt_framework.widgets.simple import ComboFactory

LOCALES_PATH = Path('./locales')
DEFAULT_LOCALE = 'ru'
LOCALES = [DEFAULT_LOCALE] + find_locales(LOCALES_PATH)


class GUIConfig(Storage):
    colormap: str = 'magma'  # any value from plt.colormaps()
    locale: str = DEFAULT_LOCALE

    def __post_init__(self):
        super().__init__()


class GuiModelView:
    colormap = ComboFactory(plt.colormaps())
    locale = ComboFactory(LOCALES)


class GuiModel(Model):
    colormap = Field(GuiModelView.colormap, default='magma', verbose_name=QT_TR_NOOP('Цвет. схема'))
    locale = Field(GuiModelView.locale, default=DEFAULT_LOCALE, verbose_name=QT_TR_NOOP('Язык'))


GUISettingsWidget = create_model_widget
