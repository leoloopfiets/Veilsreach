from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout

from .sidebar import Sidebar
from ..appstate import AppState
from .menubar import MenuBar
from .bottombar import BottomBar

class MainWindow(QMainWindow):
    def __init__(self, state: AppState):
        super().__init__()
        self.setWindowTitle("Dungeon Builder")

        self.state = state

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(Sidebar(self.state))
        main_layout.addWidget(self.state.view, 1)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(MenuBar(self.state))
        layout.addLayout(main_layout)
        layout.addWidget(BottomBar(self.state))