from sys import argv


def run(path_list=None):  # pragma: no cover
    from pathlib import Path
    from configparser import ConfigParser
    from ctypes import windll as ctypes_windll
    from sys import exit as sys_exit

    from PySide6.QtWidgets import QApplication as QtWidgets_QApplication
    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool import FOLDER
    from GHEtool.gui.gui_combine_window import MainWindow
    from GHEtool import ghe_logger

    # init application
    app = QtWidgets_QApplication()
    # get current version
    path = Path(FOLDER).parent
    config = ConfigParser()
    config.read_file(open(path.joinpath('setup.cfg'), 'r'))
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
    if path_list is not None:
        main_window.filename = ([path for path in path_list if path.endswith('.GHEtool')][0], 0)
        main_window.fun_load_known_filename()

    ghe_logger.addHandler(main_window.status_bar)

    # show window
    try:
        import pyi_splash
        pyi_splash.close()
    except ModuleNotFoundError:
        pass

    ghe_logger.info('GHEtool loaded!')
    window.showMaximized()
    # close app
    sys_exit(app.exec())


if __name__ == "__main__":  # pragma: no cover
    # pass system args like a file to read
    run(argv if len(argv) > 1 else None)
