from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QFileDialog, QSpinBox
from PyQt6.QtCore import QT_TR_NOOP

from helpers.pyqt.translate import QBaseWidget, QTransLabel, QTransPushButton
from pyqt_framework.storage import connect_input, Storage
from helpers.pyqt import add_items
from helpers import PathSplit
import common_data


class SavingConfig(Storage):
    _filename_template: str = "{}.wav"
    pieces_per_file: int = 100

    def __post_init__(self):
        super(SavingConfig, self).__init__()


class SavingSettingsWidget(QBaseWidget):
    def __init__(self, storage):
        super().__init__()
        self._storage = storage

        file_pieces_label = QTransLabel()
        file_pieces_label.set_orig_text(QT_TR_NOOP('Фрагм./файл'), self)

        file_pieces_input = QSpinBox()
        file_pieces_input.setRange(0, common_data.MAX_INT32)
        connect_input(file_pieces_input, storage, 'pieces_per_file')

        path_input = QLineEdit()
        connect_input(path_input, storage, '_filename_template')

        choose_dir_btn = QTransPushButton()
        choose_dir_btn.set_orig_text(QT_TR_NOOP('Выбрать директорию'), self)
        choose_dir_btn.clicked.connect(self.maybe_set_rec_dir)

        layout = add_items(
            QHBoxLayout(), (
                file_pieces_label,
                file_pieces_input,
                path_input,
                choose_dir_btn
            ), (1, 1, 8, 1)
        )
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def maybe_set_rec_dir(self):
        path = QFileDialog.getExistingDirectory(self, self.tr('Выберите директорию'))
        if path:
            # noinspection PyProtectedMember
            template = PathSplit(self._storage._filename_template)
            template.dir = path
            self._storage.set_field_value('_filename_template', str(template))
