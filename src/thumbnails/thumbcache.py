import hashlib
import os

import trimesh
from PyQt5.QtGui import QIcon, QPixmap

from .thumbgen import make_thumbnail


class ThumbnailCache:
    def __init__(self, size=64, folder="./.thumbnails"):
        self.size = size
        self.folder = folder
        os.makedirs(folder, exist_ok=True)

    def _hash(self, name):
        return hashlib.sha256(name.encode()).hexdigest()

    def get(self, mesh: trimesh.Geometry, name: str):
        h = self._hash(name)
        path = os.path.join(self.folder, h + ".png")
        if os.path.exists(path):
            return QPixmap(path)
        print(f"Generating tumbnail for {name}")
        pixmap = make_thumbnail(mesh, self.size)
        pixmap.save(path)
        return pixmap
    
    def getMeshIcon(self, mesh: trimesh.Geometry, name: str):
        return QIcon(self.get(mesh, name))
