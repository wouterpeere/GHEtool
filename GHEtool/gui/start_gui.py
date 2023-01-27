def run(): # pragma: no cover
    import pathlib
    from configparser import ConfigParser
    from ctypes import windll as ctypes_windll
    from sys import argv
    from sys import exit as sys_exit

    from PySide6.QtWidgets import QApplication as QtWidgets_QApplication
    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool import FOLDER
    from GHEtool.gui.gui_combine_window import MainWindow

    # init application
    app = QtWidgets_QApplication(argv)
    # get current version
    path = pathlib.Path(FOLDER).parent
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
    MainWindow(window, app)

    # show window
    try:
        import pyi_splash
        pyi_splash.close()
    except ModuleNotFoundError:
        pass
    window.showMaximized()
    # close app
    sys_exit(app.exec())


if __name__ == "__main__": # pragma: no cover
    run()
