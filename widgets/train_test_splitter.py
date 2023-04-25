from dataclasses import dataclass
from PyQt6.QtCore import QT_TR_NOOP, QObject
from PyQt6.QtWidgets import QDoubleSpinBox

from helpers.pyqt.translate import QBaseWidget, QTransLabel, QTransPushButton
from pyqt_framework.storage import connect_input, Storage


class SplitterConfig(Storage):
    train_test_ratio: float = 0.5


class TrainTestSplitterWidget(QBaseWidget):
    def __init__(self, splitter_config):
        super().__init__()
        train_test_ratio_label = QTransLabel()
        train_test_ratio_label.set_orig_text(QT_TR_NOOP('Обучающие данные, %'), self)

        train_test_ratio_input = QDoubleSpinBox()
        train_test_ratio_input.setRange(0, 1)
        train_test_ratio_input.setSingleStep(0.01)
        connect_input(train_test_ratio_input, splitter_config, 'train_test_ratio')

        split_data_button = QTransPushButton()
        split_data_button.set_orig_text(QT_TR_NOOP('Разделить данные'), self)
