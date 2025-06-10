import subprocess
import sys
from PyQt5.QtWidgets import QMenu, QMenuBar, QFileDialog, QMessageBox

import json

from ..world.world import WorldSerial
from ..world.worldobject import WorldObject
from ..world.worldcamera import WorldCamera
from ..appstate import AppState
from ..events import event_bus

class MenuBar(QMenuBar):
    def __init__(self, state: AppState):
        super().__init__()

        self.state = state

        self._current_filepath = None

        # stiles

        self.setStyleSheet("""
            QMenuBar {
                border-bottom: 1px solid #C0C0C0;
            }
        """)

        # file menu
        file_menu = QMenu("File", self)
        self.addMenu(file_menu)

        self.action_new = file_menu.addAction("New project")

        file_menu.addSeparator()

        self.action_load = file_menu.addAction("Open project")
        
        file_menu.addSeparator()

        self.action_save = file_menu.addAction("Save")
        self.action_save_as = file_menu.addAction("Save As")

        # Connect file menu
        self.action_new.triggered.connect(self.new_project)
        self.action_save.triggered.connect(self.save_project)
        self.action_save_as.triggered.connect(self.save_as_project)
        self.action_load.triggered.connect(self.load_project)

    def new_project(self):
        if self._return_unsaved(): return

        self._current_filepath = None
        self.state.world.resetWorld()
        event_bus.tilesChanged.emit()
        self.state.view.update()
        

    def save_project(self):
        if not self._current_filepath:
            self.save_as_project()
            return
        self._save_to_file(self._current_filepath)

    def save_as_project(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Project As", "", "Project Files (*.json)")
        if not path:
            return
        self._current_filepath = path
        self._save_to_file(path)

    def load_project(self):
        if self._return_unsaved(): return

        path, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "Project Files (*.json)")
        if not path:
            return
        self._load_from_file(path)
        self._current_filepath = path
    

    def _save_to_file(self, path):
        import json

        serial = self.state.world.serializeWorld()
        # Serialize as dict
        data = {
            "tile_meshes": serial.tile_meshes,
            "objects": [obj.to_dict() for obj in serial.objects],
            "camera": serial.camera.to_dict(),
            "grid_size": serial.grid_size,
            "grid_shown": serial.grid_shown,
            "tile_id_counter": serial.tile_id_counter,
        }

        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Save Failed", f"Could not save project:\n{e}")

    def _load_from_file(self, path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Load Failed", f"Could not load project:\n{e}")
            return

        objects = [WorldObject.from_dict(d) for d in data.get("objects", [])]

        serial = WorldSerial(
            tile_meshes=data.get("tile_meshes", {}),
            objects=objects,
            camera=WorldCamera.from_dict(data.get("camera", WorldCamera())),
            grid_size=data.get("grid_size", 50),
            grid_shown=data.get("grid_shown", True),
            tile_id_counter=data.get("tile_id_counter", 0),
        )
        
        self.state.world.resetWorld()
        self.state.stlloader.importPaths(self, serial.tile_meshes)
        self.state.world.loadWorld(serial)
        self.state.view.update()

    def _return_unsaved(self):
        reply = QMessageBox.question(
            self,
            "New Project",
            "There may be unsaved changes in the current project, continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply != QMessageBox.Yes