
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import (
    QFileDialog,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..appstate import AppState
from .toggelistwidget import ToggleListWidget
from ..events import event_bus
from src.controllers.exporter import count_tiles
from PyQt5.QtWidgets import QMessageBox

class Sidebar(QWidget):
    def __init__(self, state: AppState):
        super().__init__()

        self.state = state

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.btn_import = QPushButton("Import STL")
        layout.addWidget(self.btn_import)

        self.btn_export = QPushButton("Export")
        layout.addWidget(self.btn_export)

        self.lst_tiles = ToggleListWidget()
        layout.addWidget(self.lst_tiles)

        layout.addStretch()  # push widgets to top

        # Connect signals from sidebar
        self.lst_tiles.selected.connect(self._select)
        self.lst_tiles.deselected.connect(self._deselect)
        self.btn_import.clicked.connect(self._import)
        self.btn_export.clicked.connect(self._export)

        # Connect global events
        event_bus.tilesChanged.connect(self._onTilesChanged)

    def _onTilesChanged(self):
        self.lst_tiles.clear()
        for i, (key, tile) in enumerate(self.state.world.tile_meshes.items()):
            item = QListWidgetItem(tile.icon, tile.name)
            item.setData(Qt.UserRole, key) 
            self.lst_tiles.addItem(item)
        
    def _select(self, idx):
        item = self.lst_tiles.item(idx)
        tile_id = item.data(Qt.UserRole)
        self.state.world.selected_mesh = tile_id
        self.state.view.resetCursor()
        self.state.view.update()

    def _deselect(self):
        self.state.world.selected_mesh = None
        self.state.view.update()

    def _import(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Pick STL-Files", "", "STL Files (*.stl)")
        self.state.stlloader.importPaths(self, paths)

    def _export(self):
        # Build a list of “placed” tiles for counting:
        placed = [
           { 'tile': self.state.world.tile_meshes[obj.mesh_id] }
            for obj in self.state.world.objects
        ]
        counts = count_tiles(placed)

        # Format and show a simple summary dialog
        if counts:
            msg = "\n".join(f"{name}: {cnt}" for name, cnt in counts.items())
        else:
            msg = "No tiles placed yet."
        QMessageBox.information(self, "Tile Counts", msg)