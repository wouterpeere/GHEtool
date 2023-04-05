"""
script to start the GUI
"""
import logging
# pragma: no cover
import sys
from sys import argv
from platform import system

import ScenarioGUI.global_settings

from GHEtool.gui.gui_structure import GUI
from GHEtool.gui.gui_classes.translation_class import Translations
from GHEtool import Borefield
from GHEtool.gui.data_2_borefield_func import data_2_borefield

os_system = system()
is_frozen = getattr(sys, 'frozen', False) and os_system == 'Windows'  # pragma: no cover


def run(path_list=None):  # pragma: no cover
    if is_frozen:
        import pyi_splash
        pyi_splash.update_text('Loading .')
    from configparser import ConfigParser
    if os_system == 'Windows':
        from ctypes import windll as ctypes_windll
    from pathlib import Path
    from sys import exit as sys_exit

    if is_frozen:
        pyi_splash.update_text('Loading ..')

    from PySide6.QtWidgets import QApplication as QtWidgets_QApplication
    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool.gui.gui_classes.gui_combine_window import MainWindow
    import ScenarioGUI.global_settings as globs

    globs.load(Path(__file__).parent.joinpath("gui_config.ini"))

    if is_frozen:
        pyi_splash.update_text('Loading ...')

    # init application
    app = QtWidgets_QApplication()
    if os_system == 'Windows':
        # set version and id
        myAppID = f'GHEtool v{globs.VERSION}'  # arbitrary string
        ctypes_windll.shell32.SetCurrentProcessExplicitAppUserModelID(myAppID)
    # init window
    window = QtWidgets_QMainWindow()
    # init gui window
    main_window = MainWindow(window, app, GUI, Translations, result_creating_class=Borefield, data_2_results_function=data_2_borefield)
    if is_frozen:
        pyi_splash.update_text('Loading ...')
    # load file if it is in path list
    if path_list is not None:
        main_window.filename = ([path for path in path_list if path.endswith('.GHEtool')][0], 0)
        main_window.fun_load_known_filename()

    ghe_logger = logging.getLogger()
    ghe_logger.setLevel(logging.INFO)
    # show window
    if is_frozen:
        pyi_splash.close()

    print(ScenarioGUI.global_settings.FOLDER)
    window.showMaximized()
    # close app
    sys_exit(app.exec())


if __name__ == "__main__":  # pragma: no cover
    # pass system args like a file to read
    run(argv if len(argv) > 1 else None)
