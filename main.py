import logging
import sys

from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication

from pyqt_framework.storage import connect_output, connect_json_file
from helpers.serialization import model_json_deserialize
from widgets.gui_settings import DEFAULT_LOCALE, LOCALES_PATH
from widgets.runner import RunnerWindow, RunnerConfig

SETTINGS_FILENAME = './config/settings.json'


def load_translator(app, translator, locale: str):
    if locale == DEFAULT_LOCALE:
        app.removeTranslator(translator)
        logging.info(f'set default locale ({locale})')
    else:
        if translator.load(locale, str(LOCALES_PATH)):
            logging.info(f'locale {locale} loaded')
            app.installTranslator(translator)
        else:
            logging.error(f'locale {locale} not loaded')


def main():
    logging.basicConfig(level=logging.INFO)
    settings = model_json_deserialize(RunnerConfig, SETTINGS_FILENAME)  # type: RunnerConfig
    connect_json_file(settings, SETTINGS_FILENAME)

    app = QApplication(sys.argv)
    translator = QTranslator()
    connect_output(settings.gui_config, 'locale', lambda l: load_translator(app, translator, l))

    ui = RunnerWindow(settings)
    ui.show()
    app.exec()


if __name__ == '__main__':
    main()
