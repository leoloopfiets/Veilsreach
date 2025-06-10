import math
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QProgressDialog,
    QWidget,
)

from ..world.world import World
from ..resources import meshlogic
from ..resources.tilemesh import TileData
from ..thumbnails.thumbcache import ThumbnailCache
from ..events import event_bus

class STLLoader():

    def __init__(self, world: World):
        self.world = world

        self.thumbcache: ThumbnailCache = ThumbnailCache()
        self._abort_import = False

    def importPaths(self, parent: QWidget, paths: list[str] | dict[int, str]):
        if not paths:
            return

        total = len(paths) * 4
        dlg = QProgressDialog(parent)
        dlg.setWindowTitle("Importing tiles...")
        dlg.setLabelText("Starting import...")
        dlg.setMinimum(0)
        dlg.setMaximum(total)
        dlg.setWindowModality(Qt.WindowModal)
        dlg.setCancelButtonText("Abort")
        dlg.setAutoClose(False)
        dlg.setAutoReset(False)
        dlg.show()

        self._abort_import = False

        def on_abort():
            self._abort_import = True
        dlg.canceled.connect(on_abort)
        dlg.finished.connect(on_abort)
        dlg.rejected.connect(on_abort)

        if isinstance(paths, dict):
            for i, (key, path) in enumerate(paths.items()):
                if self._abort_import:
                    break
                self.importOne(path, dlg, i, int(key))
                dlg.setValue(i * 4 + 4)
        else:
            for i, path in enumerate(paths):
                if self._abort_import:
                    break
                self.importOne(path, dlg, i, None)
                dlg.setValue(i * 4 + 4)

        dlg.close()


    def importOne(self, path: str, dlg: QProgressDialog, dlgi: int, tilei: int | None):
        filename = os.path.basename(path)

        if self.world.getTile(path) != None and tilei == None:
            return  # skip duplicates

        # Load mesh
        if (dlg): dlg.setLabelText(f"Loading mesh: {filename}")
        QApplication.processEvents()
        raw_mesh = meshlogic.loadMesh(path)
        if (dlg): dlg.setValue(dlgi * 4 + 1)

        # Create bounding box
        if (dlg): dlg.setLabelText(f"Analyzing mesh: {filename}")
        QApplication.processEvents()
        bb = meshlogic.createBoundingBox(raw_mesh)
        dims = meshlogic.createDims(bb)
        if (dlg): dlg.setValue(dlgi * 4 + 2)

        # Reduce mesh
        if (dlg): dlg.setLabelText(f"Reducing mesh: {filename}")
        QApplication.processEvents()
        max_faces = min(5000 * (max(round(math.log2(max(dims.vol, 2))), 1)), 25000)
        print(f"maxf {filename} [{max_faces} from {raw_mesh.faces.shape[0]}] v: {dims.vol}")
        mesh = meshlogic.reduceMesh(raw_mesh, max_faces)
        if (dlg): dlg.setValue(dlgi * 4 + 3)

        # Create tumbnail
        if (dlg): dlg.setLabelText(f"Generating thumbnail: {filename}")
        QApplication.processEvents()
        icon = self.thumbcache.getMeshIcon(mesh, path)
        if (dlg): dlg.setValue(dlgi * 4 + 4)

        # Register tile
        tilename = f"{filename.replace(' ', '_')} [{dims.serialize()}]"
        tile = TileData(path, tilename, mesh, bb, dims, icon)
        self._registerTile(tile, tilei)

    def _registerTile(self, tile: TileData, tilei: int | None):
        self.world.registerTile(tile, tilei)
        event_bus.tilesChanged.emit()
        