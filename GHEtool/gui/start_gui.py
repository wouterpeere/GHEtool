def run():
    from ctypes import windll as ctypes_windll
    from sys import argv
    from sys import exit as sys_exit

    from PySide6.QtWidgets import QApplication as QtWidgets_QApplication
    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    from GHEtool.gui.gui_combine_window import MainWindow

    # init application
    app = QtWidgets_QApplication(argv)
    # Create and display the splash screen
    myAppID = 'GHEtool v2.1.0'  # arbitrary string
    ctypes_windll.shell32.SetCurrentProcessExplicitAppUserModelID(myAppID)
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


if __name__ == "__main__":
    run()
