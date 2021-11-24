from sys import argv, exit as sys_exit
from PyQt5.QtWidgets import QApplication as QtWidgets_QApplication
from Gui_window import MainWindow
from PyQt5.QtWidgets import QWidget as QtWidgets_QWidget
from ctypes import windll as ctypes_windll
from IconClass import IconClass
# init application
app = QtWidgets_QApplication(argv)
IC = IconClass()
# Create and display the splash screen
myAppID = 'GHEtool.0.9'  # arbitrary string
ctypes_windll.shell32.SetCurrentProcessExplicitAppUserModelID(myAppID)
# init window
window = QtWidgets_QWidget()
# init GUI window
ui_window = MainWindow(window, app)
# show window
try:
    import pyi_splash
    pyi_splash.close()
except ModuleNotFoundError:
    pass
window.show()
# close app
sys_exit(app.exec_())
