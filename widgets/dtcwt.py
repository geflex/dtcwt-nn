from dataclasses import dataclass
from enum import Enum

import dtcwt.defaults
import numpy as np
from PyQt6.QtCore import QT_TR_NOOP, QObject
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QSpinBox, QVBoxLayout

import common_data
import features
from helpers.pyqt import add_items
from pyqt_framework.model import Field
from pyqt_framework.widgets.simple import ComboFactory, CheckBoxFactory
from pyqt_framework.storage import connect_input, Storage
from helpers.pyqt.translate import (QBaseWidget, QFormatableLabel,
                                    QTransCheckBox, QTransLabel)
from widgets.feature import Feature, FixedFragmentFeature
from widgets.log_spin import QLogSpinBox


class BiortWavelets(Enum):
    antonini = 'antonini'
    legall = 'legall'
    near_sym_a = 'near_sym_a'
    near_sym_b = 'near_sym_b'


class QShiftWavelets(Enum):
    qshift_06 = 'qshift_06'
    qshift_a = 'qshift_a'
    qshift_b = 'qshift_b'
    qshift_c = 'qshift_c'
    qshift_d = 'qshift_d'


BIORT_WAVELETS = [e.value for e in BiortWavelets]
QSHIFT_WAVELETS = [e.value for e in QShiftWavelets]


class DTCWT(Storage, Feature):
    biort: str = dtcwt.defaults.DEFAULT_BIORT
    qshift: str = dtcwt.defaults.DEFAULT_QSHIFT
    levels: int = 1
    fragment_len: int = 1024
    include_original: bool = False
    include_cj: bool = False

    def __post_init__(self):
        super().__init__()

    @property
    def feature_size(self) -> tuple[int, int]:
        return features.dtcwt_shape(self.fragment_len, self.levels,
                                    self.include_original, self.include_cj)

    def __call__(self, sample):
        scalogram = features.dtcwt(sample, self.levels, self.include_original,
                                   self.include_cj, self.biort, self.qshift)
        return features.normalize(scalogram)

    def validate(self) -> list[str]:
        errors = super().validate()
        if np.log2(self.fragment_len) % 1 != 0:
            errors.append(f'Длина фрагмента ({self.fragment_len}) должна быть степенью двойки')
        if self.levels > np.log2(self.fragment_len):
            errors.append('Максимальное кол-во уровней разложения для фрагмента длины '
                          f'{self.fragment_len} равно {int(np.log2(self.fragment_len))}')
        return errors


class DtcwtModel(FixedFragmentFeature):
    # noinspection PyUnresolvedReferences
    fragment_len = FixedFragmentFeature.fragment_len.copy(default=1024)

    biort: BiortWavelets = Field(verbose_name='Biort wavelet')
    qshift: QShiftWavelets = Field(verbose_name='Q-Shift wavelet')
    levels: int = Field(default=1, verbose_name='Levels count')
    include_original: bool = Field(CheckBoxFactory(), default=False, verbose_name='Include original')
    include_cj: bool = Field(CheckBoxFactory(), default=False, verbose_name='Include cj')

    @property
    def feature_size(self) -> tuple[int, int]:
        return features.dtcwt_shape(self.fragment_len, self.levels,
                                    self.include_original, self.include_cj)

    def __call__(self, sample):
        scalogram = features.dtcwt(sample, self.levels, self.include_original,
                                   self.include_cj, self.biort, self.qshift)
        return features.normalize(scalogram)

    def validate(self) -> list[str]:
        errors = super().validate()
        if np.log2(self.fragment_len) % 1 != 0:
            errors.append(f'Длина фрагмента ({self.fragment_len}) должна быть степенью двойки')
        if self.levels > np.log2(self.fragment_len):
            errors.append('Максимальное кол-во уровней разложения для фрагмента длины '
                          f'{self.fragment_len} равно {int(np.log2(self.fragment_len))}')
        return errors


def dtcwt_shape_label(parent: QObject, feature: DTCWT):
    feature_shape_label = QFormatableLabel()
    feature_shape_label.set_orig_text(QT_TR_NOOP('Размер скейлограммы: {}'), parent)

    def update_feature_info(*args, **kwargs):
        feature_shape_label.set_fmt_values(feature.feature_size)

    feature.levels_changed.connect(update_feature_info)
    feature.fragment_len_changed.connect(update_feature_info)
    feature.include_original_changed.connect(update_feature_info)
    feature.include_cj_changed.connect(update_feature_info)

    update_feature_info()

    return feature_shape_label


class DtcwtWidget(QBaseWidget):
    def __init__(self, feature: DTCWT):
        super().__init__()
        self.init_ui(feature)

    def init_ui(self, feature: DTCWT):
        biort_label = QTransLabel()
        biort_label.set_orig_text(QT_TR_NOOP('Вейвлет 1'), self)

        biort_combobox = QComboBox()
        biort_combobox.addItems(BIORT_WAVELETS)
        biort_combobox.setCurrentText(feature.biort)
        biort_combobox.currentTextChanged.connect(lambda v: setattr(feature, 'biort', v))

        qshift_label = QTransLabel()
        qshift_label.set_orig_text(QT_TR_NOOP('Вейвлет 2'), self)

        qshift_combobox = QComboBox()
        qshift_combobox.addItems(QSHIFT_WAVELETS)
        qshift_combobox.setCurrentText(feature.qshift)
        qshift_combobox.currentTextChanged.connect(lambda v: setattr(feature, 'qshift', v))

        # Other feature settings
        dec_levels_label = QTransLabel()
        dec_levels_label.set_orig_text(QT_TR_NOOP('Кол-во уровней'), self)
        dec_levels_input = QSpinBox()
        connect_input(dec_levels_input, feature, 'levels')

        fragment_len_label = QTransLabel()
        fragment_len_label.set_orig_text(QT_TR_NOOP('Длина фрагмента'), self)
        self.fragment_len_input = QLogSpinBox()
        self.fragment_len_input.setRange(4, common_data.MAX_INT32)
        connect_input(self.fragment_len_input, feature, 'fragment_len')

        include_orig_checkbox = QTransCheckBox()
        include_orig_checkbox.set_orig_text(QT_TR_NOOP('Добавлять оригинал'), self)
        connect_input(include_orig_checkbox, feature, 'include_original')

        include_cj_checkbox = QTransCheckBox()
        include_cj_checkbox.set_orig_text(QT_TR_NOOP('Добавлять cj'), self)
        connect_input(include_cj_checkbox, feature, 'include_cj')

        feature_layout = QVBoxLayout()
        feature_layout.setContentsMargins(0, 0, 0, 0)
        add_items(feature_layout, (
            add_items(QHBoxLayout(), (biort_label, biort_combobox)),
            add_items(QHBoxLayout(), (qshift_label, qshift_combobox)),
            add_items(QHBoxLayout(), (dec_levels_label, dec_levels_input)),
            add_items(QHBoxLayout(), (fragment_len_label, self.fragment_len_input)),
            include_orig_checkbox,
            include_cj_checkbox,
        ))

        self.setLayout(feature_layout)
