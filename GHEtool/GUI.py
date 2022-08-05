def run():
    from sys import argv, exit as sys_exit
    from PyQt5.QtWidgets import QApplication as QtWidgets_QApplication
    from gui.Gui_window import MainWindow
    from PyQt5.QtWidgets import QMainWindow as QtWidgets_QMainWindow
    from ctypes import windll as ctypes_windll
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
    sys_exit(app.exec_())


if __name__ == "__main__":
    run()
