from typing import Callable, Any
from PyQt6.QtCore import QEvent, pyqtSignal, QObject
from PyQt6.QtWidgets import QLabel, QMainWindow, QCheckBox, QPushButton, QWidget


class QBaseWidget(QWidget):
    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)

    def retranslate_ui(self):
        pass

    def create_layout(self):
        pass

    def connect_ui(self, *args, **kwargs):
        pass


class QBaseWindow(QMainWindow, QBaseWidget):
    closed = pyqtSignal()

    def set_orig_window_title(self, title: str, tr_obj: QObject):
        self._orig_window_title = title
        self._tr_obj = tr_obj
        self.setWindowTitle(tr_obj.tr(self._orig_window_title))

    def closeEvent(self, a0) -> None:
        self.closed.emit()
        return super().closeEvent(a0)

    def retranslate_ui(self):
        self.setWindowTitle(self._tr_obj.tr(self._orig_window_title))


class QTranslatableText(QBaseWidget):
    text: Callable[[], str]
    setText: Callable[[str], None]
    _orig_text = None

    def set_orig_text(self, text: str, tr_obj: QObject):
        self._tr_obj = tr_obj
        self._orig_text = text
        return self.retranslate_ui()

    def retranslate_ui(self):
        if self._orig_text:
            text = self._tr_obj.tr(self._orig_text)
            self.setText(text)
            return text


class QTransCheckBox(QCheckBox, QTranslatableText):
    pass


class QTransPushButton(QPushButton, QTranslatableText):
    pass


class QTransLabel(QLabel, QTranslatableText):
    pass


class QFormatableText(QTranslatableText):
    _FMT_VALUE_NOT_SET = object()
    _fmt_text = None
    _fmt_args_count: int = 0
    _fmt_values = _FMT_VALUE_NOT_SET

    def set_orig_text(self, text: str, tr_obj: QObject):
        self._fmt_text = tr_obj.tr(text)
        self._fmt_args_count = text.count('{}')
        return super().set_orig_text(text, tr_obj)

    def set_fmt_values(self, *fmt_values: Any):
        self._fmt_values = fmt_values
        self.update_ui()

    def retranslate_ui(self):
        self._fmt_text = self._tr_obj.tr(self._orig_text)
        self.update_ui()

    def update_ui(self):
        if self._orig_text:
            if self._fmt_values is self._FMT_VALUE_NOT_SET:
                self._fmt_values = [''] * self._fmt_args_count
            text = self._fmt_text.format(*self._fmt_values)
            self.setText(text)


class QFormatableLabel(QLabel, QFormatableText):
    pass
