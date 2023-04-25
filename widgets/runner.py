import enum
import time
import warnings
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd
from PyQt6 import QtGui
from PyQt6.QtCore import pyqtSignal, QT_TR_NOOP, QThread, QObject
from PyQt6.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout, QSpinBox, QLabel, QProgressBar, \
    QErrorMessage, QFileDialog
from scipy import io as sio
from tensorflow import keras

import common_data
from helpers.keras import get_model_input_shape, get_model_output_shape
from helpers.pyqt import add_items, create_filter, add_worker_to_thread
from pyqt_framework.storage import connect_output, connect_input, Storage
from helpers.pyqt.translate import QBaseWindow, QTransPushButton, QTransLabel, QTransCheckBox, \
    QFormatableLabel
from helpers.serialization import model_json_deserialize
from pyqt_framework.model import Model, Field
from pyqt_framework.widgets.model_editor import ModelEditorFactory, create_layout
from pyqt_framework.widgets.path import PathEditFactory, OpenFilenamesFactory
from pyqt_framework.widgets.simple import CheckBoxFactory, IntSpinFactory, LineEditFactory
from widgets.class_probabilities import ClassProbabilitiesWidget
from widgets.display import Display2DWidget
from widgets.gui_settings import GUIConfig
from widgets.model_info import ModelConfig
from widgets.saving_settings import SavingSettingsWidget


class RunnerSource(enum.IntEnum):
    none = 0
    microphone = 1
    files = 2


class RunnerConfig(Storage):
    microphone: bool = True
    display: bool = True  # consumer of dtcwt
    classify: bool = False  # consumer of dtcwt

    model_path: str = ''
    model_config_path: str = ''

    max_pieces: int = 100

    filenames: list = ()
    pieces_per_file: int = 100
    _filename_template: str = '{}.wav'

    gui_config: GUIConfig = GUIConfig()

    # model: Optional[keras.models.Model] = None
    # model_config: Optional[ModelConfig] = None

    model_changed = pyqtSignal(keras.models.Model)
    model_config_changed = pyqtSignal(object)

    def __post_init__(self):
        super().__init__()

    def validate(self) -> list[str]:
        model_config = self.model_config
        errors = model_config.validate()
        if self.classify and model_config.feature.feature_size != get_model_input_shape(self.model):
            errors.append(f'Размер скейлограммы {model_config.feature.feature_size}'
                          f' не равен входному размеру модели {get_model_input_shape(self.model)}')
        if self.microphone and not self.any_consumer_enabled and not self.should_save:
            errors.append('Некуда подавать данные: скейлограмма, диагностика '
                          'и сохранение файлов отключены')
        if not self.microphone and not self.any_consumer_enabled:
            errors.append('Некуда подавать данные: скейлограмма и диагностика отключены')
        if get_model_output_shape(self.model) != len(model_config.classnames):
            errors.append('Количество классов не соответствует выходу модели')
        return errors

    @property
    def source(self) -> RunnerSource:
        if self.microphone and (self.should_save or self.any_consumer_enabled):
            return RunnerSource.microphone
        if not self.microphone and self.any_consumer_enabled:
            return RunnerSource.files
        return RunnerSource.none

    @property
    def any_consumer_enabled(self) -> bool:
        return any((self.display, self.classify))

    @property
    def should_save(self):
        return self.pieces_per_file > 0 and self.microphone

    @property
    def auto_stop_enabled(self):
        return bool(self.max_pieces)

    def load_model(self, path: str):
        self.model_path = path
        model = keras.models.load_model(path)
        self.set_field_value('model', model)

    def load_model_config(self, path: str):
        self.model_config_path = path
        config = model_json_deserialize(ModelConfig, self.model_config_path)
        self.set_field_value('model_config', config)

    def classify_piece(self, feature) -> np.array:
        feature = np.expand_dims(feature, axis=(0, -1))
        return self.model.predict(feature)[0]  # shape = (num_classes, )


class RunnerModel(Model):
    microphone = Field(CheckBoxFactory(), default=True)
    display = Field(CheckBoxFactory(), default=True)
    classify = Field(CheckBoxFactory(), default=True)

    model_path = Field(PathEditFactory(QT_TR_NOOP('Загрузить модель')))
    model_config_path = Field(PathEditFactory(QT_TR_NOOP('Загрузить конфигурацию')))

    max_pieces = Field(IntSpinFactory(), default=100)

    filenames = Field(OpenFilenamesFactory(QT_TR_NOOP('Открыть файлы')), default=())
    pieces_per_file = Field(IntSpinFactory(), default=100, verbose_name=QT_TR_NOOP('Фрагм./файл'))
    _filename_template: str = Field(LineEditFactory(), default='{}.wav')

    gui_config = Field(ModelEditorFactory(), default=GUIConfig)

    # model: Optional[keras.models.Model] = None
    # model_config: Optional[ModelConfig] = None

    model = Field()
    model_config = Field()


RESOURCES_PATH = Path('./resources')


class RunnerWindow(QBaseWindow):
    def __init__(self, settings: RunnerConfig):
        super().__init__()
        self.settings = settings

        self.settings_window = None  # type: Optional[QBaseWindow]

        self.setWindowIcon(QtGui.QIcon(str(RESOURCES_PATH / 'icon.png')))

        main_layout = add_items(QHBoxLayout(), (
            self.create_class_pane(),
            self.create_nav_pane(),
        ))

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.set_orig_window_title(QT_TR_NOOP('Акустическая диагностика'), self)
        self.connect_ui(self.settings)

    def open_fitter(self):
        self.fitter_window = QBaseWindow(self)
        self.fitter_window.set_orig_window_title(QT_TR_NOOP('Обучение'), self)
        widget = QWidget()
        widget.setLayout(create_layout(self.settings.fit_model))
        self.fitter_window.setCentralWidget(widget)
        self.fitter_window.show()

    def create_class_pane(self):
        self.classes_widget = ClassProbabilitiesWidget()
        connect_output(self.settings, 'classify', self.classes_widget.setVisible)

        class_pane_layout = QVBoxLayout()
        class_pane_layout.setContentsMargins(0, 0, 0, 0)
        class_pane_layout.addWidget(self.classes_widget)
        class_pane_layout.addStretch()

        # load config + update class pane
        self.settings.model_changed.connect(
            lambda m: setattr(self.classes_widget, 'classes_count', get_model_output_shape(m))
        )
        self.settings.model_config_changed.connect(
            lambda conf: self.classes_widget.update_classnames(conf.classnames)
        )
        self.settings.load_model(self.settings.model_path)
        self.settings.load_model_config(self.settings.model_config_path)
        self.settings.model_config.classnames_changed.connect(self.classes_widget.update_classnames)
        return class_pane_layout

    def create_nav_pane(self):
        self.settings_button = QTransPushButton()
        self.settings_button.set_orig_text(QT_TR_NOOP('Настройки'), self)
        self.settings_button.setShortcut('Ctrl+,')

        self.start_button = QTransPushButton()
        self.start_button.set_orig_text(QT_TR_NOOP('Старт'), self)
        self._start_shortcut = 'F5'
        self.start_button.setCheckable(True)
        self.start_button.setShortcut(self._start_shortcut)

        max_pieces_label = QTransLabel()
        max_pieces_label.set_orig_text(QT_TR_NOOP('Авто-стоп'), self)
        max_pieces_input = QSpinBox()
        max_pieces_input.setRange(0, common_data.MAX_INT32)
        connect_input(max_pieces_input, self.settings, 'max_pieces')

        self.fitter_button = QTransPushButton()
        self.fitter_button.set_orig_text(QT_TR_NOOP('Обучение'), self)

        # # Checkboxes
        self.microphone_checkbox = QTransCheckBox()
        self.microphone_checkbox.set_orig_text(QT_TR_NOOP('Микрофон'), self)
        self.microphone_checkbox.setShortcut('Ctrl+M')

        self.image_updating_checkbox = QTransCheckBox()
        self.image_updating_checkbox.set_orig_text(QT_TR_NOOP('Дисплей'), self)
        self.image_updating_checkbox.setShortcut('Ctrl+D')

        self.classify_checkbox = QTransCheckBox()
        self.classify_checkbox.set_orig_text(QT_TR_NOOP('Классификация'), self)
        self.classify_checkbox.setShortcut('Ctrl+K')

        self.checkboxes_widget = QWidget()  # needed for disabling all checkboxes
        checkboxes_layout = QHBoxLayout(self.checkboxes_widget)
        checkboxes_layout.setContentsMargins(0, 0, 0, 0)
        add_items(checkboxes_layout, (
            self.microphone_checkbox,
            self.image_updating_checkbox,
            self.classify_checkbox,
        ))

        # # file progress
        self.file_progress_widget = QWidget()

        self.file_progress_label = QFormatableLabel()
        self.file_progress_label.set_orig_text(QT_TR_NOOP('Файл: {}/{}, фрагмент: {}/{}'), self)
        self.filename_label = QLabel()
        self.file_progress_layout = QHBoxLayout(self.file_progress_widget)
        self.file_progress_layout.setContentsMargins(0, 4, 0, 4)
        add_items(self.file_progress_layout, (
            self.file_progress_label,
            self.filename_label,
        ))

        # # Progress, Speed
        self.speed_label = QFormatableLabel()
        self.speed_label.set_orig_text(QT_TR_NOOP('Скорость: {} Гц'), self)
        self.update_speed_info(0)
        self.progressbar = QProgressBar()
        self.progressbar.setValue(0)
        self.progress_layout = add_items(QHBoxLayout(), (
            self.speed_label,
            self.progressbar,
        ))
        self.file_progress_label.set_fmt_values(0, 0, 0, 0)

        self.recorder_button = QTransPushButton()
        self.recorder_button.set_orig_text(QT_TR_NOOP('Источник'), self)

        self.feature_button = QTransPushButton()
        self.feature_button.set_orig_text(QT_TR_NOOP('Извлечение признаков'), self)

        self.splitter_button = QTransPushButton()
        self.splitter_button.set_orig_text(QT_TR_NOOP('Разделение'), self)

        self.fitter_button = QTransPushButton()
        self.fitter_button.set_orig_text(QT_TR_NOOP('Обучение'), self)

        self.display = Display2DWidget(self.settings.gui_config)

        self.saving_settings_widget = SavingSettingsWidget(self.settings)

        self.start_layout = add_items(QHBoxLayout(), (
            self.settings_button,
            self.start_button,
            max_pieces_label, max_pieces_input,
        ), (1, 8, 1, 1))

        self.other_buttons_layout = add_items(QHBoxLayout(), (
            self.recorder_button,
            self.feature_button,
            self.splitter_button,
            self.fitter_button,
        ))
        self.other_buttons_layout.setContentsMargins(0, 0, 0, 0)

        nav_pane_layout = QVBoxLayout()
        nav_pane_layout.addStretch()
        add_items(nav_pane_layout, (
            self.display,
            self.start_layout,
            self.checkboxes_widget,
            self.saving_settings_widget,
            self.file_progress_widget,
            self.progress_layout,
            # self.other_buttons_layout,
        ))
        return nav_pane_layout

    def connect_ui(self, settings):
        self.settings_button.clicked.connect(self.toggle_settings)
        self.start_button.toggled.connect(self.start_clicked)
        self.recorder_button.clicked.connect(self.open_recorder)
        self.feature_button.clicked.connect(self.open_feature_extractor)
        self.splitter_button.clicked.connect(self.open_splitter)
        self.fitter_button.clicked.connect(self.open_fitter)

        connect_input(self.microphone_checkbox, settings, 'microphone')
        connect_input(self.image_updating_checkbox, settings, 'display')
        connect_input(self.classify_checkbox, settings, 'classify')

        connect_output(settings, 'microphone', self.file_progress_widget.setHidden)
        connect_output(settings, 'display', self.display.setVisible)
        connect_output(settings, 'microphone', self.saving_settings_widget.setVisible)

    def open_recorder(self):
        # self.recorder_ui = ModelEditorFactory()(self.settings)
        # self.recorder_ui.show()
        pass

    def open_feature_extractor(self):
        pass

    def open_splitter(self):
        pass

    def start_clicked(self, process_started: bool):
        if process_started:
            errors = self.settings.validate()
            if errors:
                for error in errors:
                    error_message = QErrorMessage(self)
                    error_message.showMessage(error)
                self.start_button.setChecked(False)
                return
        text = self.tr('Стоп') if process_started else self.tr('Старт')
        self.start_button.setText(text)
        self.start_button.setShortcut(self._start_shortcut)
        self.microphone_checkbox.setDisabled(process_started)
        if self.settings_window:
            self.settings_widget.runner_settings.set_processing_started(process_started)

        if process_started:
            if self.settings.source == RunnerSource.files:
                filenames, filt = QFileDialog.getOpenFileNames(
                    self, self.tr('Выберите файлы для классификации'),
                    filter=create_filter('wav'),
                )
                if filenames:
                    self.settings.set_field_value('filenames', filenames)

            self.worker, self.thread = self.init_classifier_worker()

            self.thread.start()
        else:
            try:
                self.worker.soft_stop.emit()
            except (RuntimeError, AttributeError):
                pass

    def init_classifier_worker(self):
        worker = RunnerWorker(self.settings)
        worker.file_progress.connect(self.update_file_progress)
        worker.feature_extracted.connect(self.display.update_image)
        worker.piece_classified.connect(self.classes_widget.update_probabilities)
        worker.autostop_progress.connect(self.progressbar.setValue)
        worker.speed.connect(self.update_speed_info)
        thread = QThread()
        add_worker_to_thread(thread, worker)
        thread.finished.connect(lambda: self.start_button.setChecked(False))
        thread.finished.connect(lambda: self.progressbar.setValue(0))
        return worker, thread

    def update_file_progress(self, filename: str, i_file: int, files_total: int, i_chunk: int, chunks_in_file: int):
        self.filename_label.setText(filename)
        self.file_progress_label.set_fmt_values(i_file, files_total, i_chunk, chunks_in_file)
        if not self.settings.auto_stop_enabled and files_total != 0:
            self.progressbar.setValue(int(i_file / files_total * 100))

    def update_speed_info(self, speed: float):
        self.speed_label.set_fmt_values(int(speed))

    def toggle_settings(self):
        if not self.settings_window:
            self.settings_window = self.init_settings_window()
            self.settings_window.show()
        else:
            self.settings_window.close()

    def init_settings_window(self):
        from widgets.settings import SettingsWidget

        self.settings_widget = SettingsWidget(self.settings)
        settings_window = QBaseWindow(self)
        settings_window.setCentralWidget(self.settings_widget)
        settings_window.set_orig_window_title(QT_TR_NOOP('Настройки'), self)
        settings_window.closed.connect(lambda: setattr(self, 'settings_window', None))
        return settings_window


def get_microphone_chunks(chunk_len: int, fs: int):
    # def cb(indata, frames, t, status):
    #     if status:
    #         print(status)
    with sd.InputStream(fs, chunk_len, channels=1) as stream:
        while True:
            data, overflowed = stream.read(chunk_len)
            yield data.reshape((chunk_len, ))


FileProgress = namedtuple('FileProgress', 'filename, i_file, total_files, i_fragment, total_fragments')


class RunnerWorker(QObject):
    file_progress = pyqtSignal(str, int, int, int, int)
    feature_extracted = pyqtSignal(np.ndarray)
    piece_classified = pyqtSignal(np.ndarray)
    autostop_progress = pyqtSignal(float)
    speed = pyqtSignal(float)

    finished = pyqtSignal()

    soft_stop = pyqtSignal()

    def __init__(self, config: RunnerConfig):
        super().__init__()
        self.config = config
        self.stop_received = False
        # noinspection PyUnresolvedReferences
        self.soft_stop.connect(lambda: setattr(self, 'stop_received', True))

    def create_source(self):
        s = self.config
        if s.source == RunnerSource.microphone:
            return get_microphone_chunks(s.model_config.feature.fragment_len, s.model_config.fs)
        elif s.source == RunnerSource.Source.files:
            return self.get_file_chunks()
        else:
            return []

    def run(self):
        compute_speed_interval = 1
        paths = self.config._filename_template  # noqa
        s = self.config

        def save(fragments, total_recorded_):
            sio.wavfile.write(paths.format(total_recorded_), s.model_config.fs, fragments)

        pieces = self.create_source()
        pieces_to_save = []
        accum = np.zeros(len(s.model_config.classnames))
        total_classified = 0
        last_total_4speed = 0
        last_speed_update_time = time.time()
        for total_recorded, piece in enumerate(pieces, start=1):
            if self.stop_received:
                break
            # auto stop + saving tail
            if s.auto_stop_enabled and (total_recorded > s.max_pieces):
                if s.should_save and len(pieces_to_save):
                    save(pieces_to_save, total_recorded)
                break
            # saving
            if s.should_save:
                pieces_to_save = np.append(pieces_to_save, piece)
                if total_recorded % s.pieces_per_file == 0:
                    save(pieces_to_save, total_recorded)
                    pieces_to_save = []
            # dtcwt
            if s.any_consumer_enabled:
                feature = s.model_config.feature(piece)
                if s.display:
                    self.feature_extracted.emit(feature)
                if s.classify:
                    predictions = s.classify_piece(feature)
                    accum += predictions
                    total_classified += 1
                    self.piece_classified.emit(accum / total_classified)
            # progress
            if s.auto_stop_enabled:
                self.autostop_progress.emit(total_recorded / s.max_pieces * 100)
            # speed
            curr_time = time.time()
            if curr_time - last_speed_update_time > compute_speed_interval:
                self.speed.emit(
                    1 / ((curr_time - last_speed_update_time) / (total_recorded - last_total_4speed)) * s.model_config.feature.fragment_len
                )  # frequency
                last_total_4speed = total_recorded
                last_speed_update_time = curr_time

        self.finished.emit()

    def get_file_chunks(self):
        s = self.config
        chunk_len = s.model_config.feature.fragment_len
        fs = s.model_config.fs

        for i_file, filename in enumerate(s.filenames, start=1):
            filename = Path(filename)
            if filename.is_file():
                rate, sound = sio.wavfile.read(filename)
                if rate != fs and s.classify:
                    warnings.warn(f'{filename} rate is {rate}, but {fs} is needed')
                tail_len = len(sound) % chunk_len
                if tail_len != 0:
                    sound = sound[:-tail_len]
                pieces = sound.reshape(-1, chunk_len)
                for i_piece, piece in enumerate(pieces, start=1):
                    self.file_progress.emit(str(filename),
                                            i_file, len(s.filenames),
                                            i_piece, len(pieces))
                    yield piece