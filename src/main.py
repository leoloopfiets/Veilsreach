import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from .appstate import newAppState
from .events import KeyFilter
from .window.mainwindow import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("res/icons/favicon.ico"))
    key_filter = KeyFilter()
    app.installEventFilter(key_filter)
    state = newAppState()

    w = MainWindow(state)
    # w.resize(2560, 1440)
    w.resize(1920, 1080)
    w.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()