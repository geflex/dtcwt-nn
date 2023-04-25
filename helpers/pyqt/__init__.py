from pathlib import Path

from typing import Sequence, Union
from PyQt6.QtWidgets import QWidget, QBoxLayout
from PyQt6.QtCore import QObject, QThread


MONOSPACE_FONT = 'Consolas'


def clear_layout(layout: QBoxLayout):
    for i in reversed(range(layout.count())):
        widget = layout.itemAt(i).widget()
        if widget:
            # noinspection PyTypeChecker
            widget.setParent(None)


def add_worker_to_thread(thread: QThread, worker: QObject):
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)

    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)


def add_items(layout: QBoxLayout, items: Sequence[Union[QWidget, QBoxLayout]], stretches=()):
    if len(stretches) != len(items):
        if not stretches:
            stretches = [0] * len(items)
        else:
            raise ValueError('items and stretches must have equal length')
    for item, stretch in zip(items, stretches):
        if isinstance(item, QWidget):
            layout.addWidget(item, stretch=stretch)
        elif isinstance(item, QBoxLayout):
            layout.addLayout(item, stretch=stretch)
    return layout


def find_locales(directory='locales', suffix='.qm'):
    path = Path('.') / directory
    if not path.exists():
        return []
    locales = []
    for file in path.iterdir():
        if file.is_file() and file.suffix == suffix:
            locales.append(file.stem)
    return locales


def create_filter(ext: str):
    return f'*.{ext};*'
