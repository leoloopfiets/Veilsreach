from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout

from ..appstate import AppState
from ..resources.icons import IconAtlas


class BottomBar(QWidget):
    def __init__(self, state: AppState):
        super().__init__()

        self.state = state

        gridIcons = IconAtlas("res/icons/ic_1.bmp", 16, 15)

        self.setStyleSheet("""
            QWidget {
                border-top: 1px solid #C0C0C0;
                background-color: #F0F0F0;
            }
            QPushButton {
                background-color: #C0C0C0;
            }
            QPushButton:checked {
                background-color: #A0A0A0;
            }
        """)

        self.showGridButton = QPushButton("", self)
        self.showGridButton.setIcon(gridIcons.at(0, 0))
        self.showGridButton.setCheckable(True)
        self.showGridButton.setChecked(True)

        self.growGridButton = QPushButton("", self)
        self.growGridButton.setIcon(gridIcons.at(2, 0))

        self.shrinkGridButton = QPushButton("", self)
        self.shrinkGridButton.setIcon(gridIcons.at(1, 0))

        self.showGridButton.setFixedSize(24, 24)
        self.growGridButton.setFixedSize(24, 24)
        self.shrinkGridButton.setFixedSize(24, 24)

        # delete button
        self.deleteButton = QPushButton("×", self)
        self.deleteButton.setToolTip("Toggle delete mode")
        self.deleteButton.setCheckable(True)
        self.deleteButton.setFixedSize(24, 24)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(3)

        layout.addStretch()  # push buttons to right
        layout.addWidget(self.showGridButton)
        layout.addWidget(self.growGridButton)
        layout.addWidget(self.shrinkGridButton)
        layout.addWidget(self.deleteButton)

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                border-top: 1px solid #C0C0C0;
                background-color: #F0F0F0;
            }
            QPushButton {
                background-color: #C0C0C0;
                border: 1px solid #888;
            }
            QPushButton:checked {
                background-color: #A0A0A0;
            }
            QPushButton:pressed {
                background-color: #707070;
            }
        """)        
        
        self.showGridButton.clicked.connect(self._toggleShowGrid)
        self.growGridButton.clicked.connect(self._growGrid)
        self.shrinkGridButton.clicked.connect(self._shrinkGrid)
        self.deleteButton.clicked.connect(self._toggleDelete)


    def _toggleShowGrid(self):
        self.state.world.grid_shown = self.showGridButton.isChecked()
        self.state.view.update()

    def _growGrid(self):
        self.state.world.growGrid()
        self.state.view.update()

    def _shrinkGrid(self):
        self.state.world.shrinkGrid()
        self.state.view.update()
    
    def _toggleDelete(self):
        # flip delete mode on/off
        self.state.world.delete_mode = self.deleteButton.isChecked()
        # force redraw so user sees immediate effect
        self.state.view.update()