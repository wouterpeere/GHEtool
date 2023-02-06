from sys import argv


def run(path=None):  # pragma: no cover
    from pathlib import Path
    from configparser import ConfigParser
    from ctypes import windll as ctypes_windll
    from sys import exit as sys_exit

    from PySide6.QtWidgets import QApplication as QtWidgets_QApplication
    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool import FOLDER
    from GHEtool.gui.gui_combine_window import MainWindow

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
    # load file if it is in path list
    if path is not None:
        main_window.filename = (path, 0)
        main_window.fun_load_known_filename()

    # show window
    try:
        import pyi_splash
        pyi_splash.close()
    except ModuleNotFoundError:
        pass
    window.showMaximized()
    # close app
    sys_exit(app.exec())


if __name__ == "__main__":  # pragma: no cover
    # pass system args like a file to read
    run([path for path in argv if path.endswith('.GHEtool')][0] if len(argv) > 1 else None)
