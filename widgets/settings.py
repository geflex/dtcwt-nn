from PyQt6.QtWidgets import QSpinBox, QHBoxLayout, QVBoxLayout, QSplitter, QFileDialog, QTabWidget
from PyQt6.QtCore import QT_TR_NOOP, QObject
from tensorflow import keras

import common_data
from widgets.runner import RunnerConfig
from helpers.pyqt import add_items, create_filter
from pyqt_framework.storage import connect_input, connect_output
from helpers.pyqt.translate import QTransPushButton, QTransLabel, QFormatableLabel, QBaseWidget
from helpers.keras import get_model_input_shape
from widgets.classnames_editor import ClassnamesEditor
from widgets.dtcwt import DtcwtWidget, dtcwt_shape_label
from widgets.model_info import model_info_message
from widgets.gui_settings import GUISettingsWidget


def create_model_shape_label(self, settings: RunnerConfig):
    model_shape_label = QFormatableLabel()
    model_shape_label.set_orig_text(QT_TR_NOOP('Размер входа модели: {}'), self)
    connect_output(settings, 'model', self.update_model_shape_info)
    return model_shape_label


def create_fragment_time_label(tr_obj: QObject, settings: RunnerConfig):
    fragment_time_label = QFormatableLabel()
    fragment_time_label.set_orig_text(QT_TR_NOOP('Длительность фрагмента: {} с'), tr_obj)

    def update(*args, **kwargs):
        fragment_len_time = settings.model_config.feature.fragment_len / settings.model_config.fs
        fragment_time_label.set_fmt_values(fragment_len_time)

    settings.model_config.feature.fragment_len_changed.connect(update)
    settings.model_config.fs_changed.connect(update)
    update()
    return fragment_time_label


class RunnerSettingsWidget(QBaseWidget):
    # TODO: block inputs when open that can cause errors if model is checked

    def __init__(self, settings: RunnerConfig):
        super().__init__()
        self._settings = settings

        self.load_model_button = QTransPushButton()
        self.load_model_button.set_orig_text(QT_TR_NOOP('Загр. модель'), self)

        self.load_config_button = QTransPushButton()
        self.load_config_button.set_orig_text(QT_TR_NOOP('Загр. конфигурацию'), self)

        self.model_info_button = QTransPushButton()
        self.model_info_button.set_orig_text(QT_TR_NOOP('Информация о модели'), self)

        self.rate_label = QTransLabel()
        self.rate_label.set_orig_text(QT_TR_NOOP('Частота дискретизации'), self)

        self.rate_input = QSpinBox()
        self.rate_input.setRange(*common_data.FS_RANGE)

        self.dtcwt_widget = DtcwtWidget(settings.model_config.feature)

        self.setLayout(self.create_layout())

    def connect_ui(self, settings, *args, **kwargs):
        self.load_model_button.clicked.connect(self.maybe_load_model)
        self.load_config_button.clicked.connect(self.maybe_load_config)
        self.model_info_button.clicked.connect(self.show_model_info)
        connect_input(self.rate_input, self._settings.model_config, 'fs')

    def create_layout(self):
        self.load_layout = add_items(QHBoxLayout(), (self.load_model_button, self.load_config_button))
        self.load_layout.setContentsMargins(0, 0, 0, 0)

        self.model_shape_label = create_model_shape_label(self, self._settings)

        return add_items(QVBoxLayout(self), (
            self.load_layout,
            self.model_info_button,
            add_items(QHBoxLayout(), (self.rate_label, self.rate_input)),
            ClassnamesEditor(self._settings.model_config),
            self.dtcwt_widget,
            create_fragment_time_label(self, self._settings),
            dtcwt_shape_label(self, self._settings.model_config.feature),
            self.model_shape_label,
            QSplitter(),
        ))

    def show_model_info(self):
        self.model_info_message = model_info_message(self, self._settings.model, self._settings.model_path)
        self.model_info_message.setWindowTitle(self.tr('Архитектура модели'))
        self.model_info_message.show()

    def update_model_shape_info(self, model: keras.models.Model):
        inp_shape = get_model_input_shape(model)
        self.model_shape_label.set_fmt_values(inp_shape)

    def maybe_load_model(self):
        caption = self.tr('Выберите модель')
        path, filt = QFileDialog.getOpenFileName(self.load_model_button, caption, filter=create_filter('h5'))
        if path:
            self._settings.load_model(path)

    def maybe_load_config(self):
        caption = self.tr('Выберите конфигурацию модели')
        path, filt = QFileDialog.getOpenFileName(self, caption, filter=create_filter('json'))
        if path:
            self._settings.load_model_config(path)

    def set_processing_started(self, started: bool):
        self.dtcwt_widget.setDisabled(started and self._settings.classify)
        self.rate_input.setDisabled(started)


class SettingsWidget(QTabWidget, QBaseWidget):
    def __init__(self, config: RunnerConfig):
        super().__init__()
        self.runner_settings = RunnerSettingsWidget(config)
        self.gui_settings = GUISettingsWidget(config.gui_config)
        try:
            # noinspection PyUnresolvedReferences
            self.gui_settings.layout().addStretch()
        except AttributeError:
            pass

        self.addTab(self.runner_settings, 'Runner')
        self.addTab(self.gui_settings, 'GUI')
