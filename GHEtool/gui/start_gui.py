"""
script to start the GUI
"""
import sys  # pragma: no cover
from sys import argv  # pragma: no cover

is_frozen = getattr(sys, 'frozen', False)  # pragma: no cover


def run(path_list=None):  # pragma: no cover
    if is_frozen:
        import pyi_splash
        pyi_splash.update_text('Loading .')
    from configparser import ConfigParser
    from ctypes import windll as ctypes_windll
    from pathlib import Path
    from sys import exit as sys_exit

    if is_frozen:
        pyi_splash.update_text('Loading ..')

    from PySide6.QtWidgets import QApplication as QtWidgets_QApplication
    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool import FOLDER
    from GHEtool.gui.gui_classes.gui_combine_window import MainWindow

    if is_frozen:
        pyi_splash.update_text('Loading ...')

    # init application
    app = QtWidgets_QApplication()
    # get current version
    config = ConfigParser()
    config.read_file(open(Path(FOLDER).parent.joinpath('setup.cfg'), 'r'))
    version = config.get('metadata', 'version')
    # set version and id
    myAppID = f'GHEtool v{version}'  # arbitrary string
    ctypes_windll.shell32.SetCurrentProcessExplicitAppUserModelID(myAppID)
    app.setApplicationName('GHEtool')
    app.setApplicationVersion(f'v{version}')
    # init window
    window = QtWidgets_QMainWindow()
    # init gui window
    main_window = MainWindow(window, app)
    if is_frozen:
        pyi_splash.update_text('Loading ...')
    # load file if it is in path list
    if path_list is not None:
        main_window.filename = ([path for path in path_list if path.endswith('.GHEtool')][0], 0)
        main_window.fun_load_known_filename()

    # show window
    if is_frozen:
        pyi_splash.close()
    window.showMaximized()
    # close app
    sys_exit(app.exec())


if __name__ == "__main__":  # pragma: no cover
    # pass system args like a file to read
    run(argv if len(argv) > 1 else None)
