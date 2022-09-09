def run():
    from ctypes import windll as ctypes_windll
    from sys import argv
    from sys import exit as sys_exit

    from GHEtool.gui.Gui_window import MainWindow
    from PySide6.QtWidgets import QApplication as QtWidgets_QApplication
    from PySide6.QtWidgets import QMainWindow as QtWidgets_QMainWindow

    # init application
    app = QtWidgets_QApplication(argv)
    # Create and display the splash screen
    myAppID = 'GHEtool.0.9'  # arbitrary string
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
