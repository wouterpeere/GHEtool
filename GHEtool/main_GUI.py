from sys import argv, exit as sys_exit
from PyQt5 import QtWidgets
from Gui_window import MainWindow

# init application
app = QtWidgets.QApplication(argv)
# init window
window = QtWidgets.QWidget()
# init GUI window
ui_window = MainWindow(window, app)
# show window
window.show()
# close app
sys_exit(app.exec_())
