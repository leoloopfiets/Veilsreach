from dataclasses import dataclass, field

import numpy as np
from ..resources.tilemesh import TileData
from .worldobject import WorldObject
from .worldcamera import WorldCamera

MAX_WORLD_GRID_SIZE = 500
MIN_WORLD_GRID_SIZE = 5

@dataclass
class WorldSerial:
    tile_meshes: dict[int, str] = field(default_factory=dict)  # mesh file paths
    objects: list[WorldObject] = field(default_factory=list)
    camera: WorldCamera = WorldCamera()
    grid_size: int = 50
    grid_shown: bool = True
    tile_id_counter: int = 0


class World():
    def __init__(self):
        self.tile_meshes: dict[int, TileData] = {}
        self.objects: list[WorldObject] = []
        self.selected_objects: list[WorldObject] = []
        self.camera: WorldCamera = WorldCamera()
        self.selected_mesh: int = None
        self.grid_size: int = 50
        self.grid_shown: bool = True
# when True, left‐click will delete instead of place
        self.delete_mode: bool = False
        
        self._tile_id_counter = 0

    # Assumes world has been reset and required meshes loaded
    def loadWorld(self, serial: WorldSerial) -> None:
        self._tile_id_counter = serial.tile_id_counter
        self.grid_size = serial.grid_size
        self.grid_shown = serial.grid_shown
        self.camera = serial.camera

        # Filter objects: keep only those whose tile mesh exists
        self.objects = [obj for obj in serial.objects if obj.mesh_id in self.tile_meshes]

    def resetWorld(self) -> None:
        for tile in self.tile_meshes.values():
            tile.dispose()  # delete GL resources

        self.tile_meshes.clear()
        self.objects.clear()
        self.selected_objects.clear()
        self.camera: WorldCamera = WorldCamera()
        self.selected_mesh = None
        self.grid_size: int = 50
        self.grid_shown: bool = True

        self._tile_id_counter = 0

    def serializeWorld(self) -> WorldSerial:
        tile_paths = {tid: tile.filepath for tid, tile in self.tile_meshes.items()}
        return WorldSerial(
            tile_meshes=tile_paths,
            objects=list(self.objects),
            camera=self.camera,
            grid_size=self.grid_size,
            grid_shown=self.grid_shown,
            tile_id_counter=self._tile_id_counter,
        )

    def registerTile(self, tile: TileData, tileIndex: int | None) -> None:
        if tileIndex is None:
            self.tile_meshes[self._tile_id_counter] = tile
            self._tile_id_counter += 1
        else:
            prev = self.tile_meshes.get(tileIndex)
            if prev != None:
                prev.dispose()
            self.tile_meshes[tileIndex] = tile
            self._tile_id_counter = max(self._tile_id_counter, tileIndex + 1)

    def getTile(self, path: str):
        for tile in self.tile_meshes.values():
            if tile.filepath == path:
                return tile
        return None

    def placeObject(self, position: list[int], rotation: int) -> None:
        if self.selected_mesh is None or self.selected_mesh >= len(self.tile_meshes):
            return
        obj = WorldObject(self.selected_mesh)
        obj.pos = self.toGrid(position)
        # ox, oy, oz = self.toGridObject(obj.mesh.bb.size, rotation=round(rotation / 90))
        # obj.pos[0] -= ox
        # obj.pos[1] -= oy
        obj.rotation = rotation
        self.objects.append(obj)

    def toGrid(self, position: list[int]) -> list[int]:
        h_grid = self.grid_size / 2
        return [round((position[0] - h_grid) / self.grid_size) * self.grid_size,
                round((position[1] - h_grid) / self.grid_size) * self.grid_size,
                round((position[2] - h_grid) / self.grid_size) * self.grid_size]

    def toGridObject(self, size: list[int], rotation: int = 0) -> list[int]:
        h_size = size / 2
        
        t_min_world_size = MIN_WORLD_GRID_SIZE / 3

        return [round((h_size[0 if rotation % 2 == 0 else 1] - t_min_world_size) / self.grid_size) * self.grid_size * (1 if rotation % 2 == 0 else -1),
                round((h_size[1 if rotation <= 1 else 0] - t_min_world_size) / self.grid_size) * self.grid_size * (1 if rotation <= 1 else -1),
                round((h_size[2] - t_min_world_size) / self.grid_size) * self.grid_size]

    def growGrid(self) -> None:
        nextSize = self.grid_size * 2
        if (nextSize - 0.00001 > MAX_WORLD_GRID_SIZE):
            return
        self.grid_size = nextSize

    def shrinkGrid(self) -> None:
        nextSize = self.grid_size / 2
        if (nextSize + 0.00001 < MIN_WORLD_GRID_SIZE):
            return
        self.grid_size = nextSize
