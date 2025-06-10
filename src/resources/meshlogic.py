from dataclasses import dataclass

import numpy as np
import trimesh


@dataclass
class WorldDims:
    size: np.ndarray  # shape (3,)
    vol: int

    def serialize(self) -> str:
        return 'x'.join(map(str, self.size.tolist()))
    
@dataclass
class BoundingBox:
    min_corner: np.ndarray  # shape (3,)
    max_corner: np.ndarray  # shape (3,)
    size: np.ndarray        # shape (3,)
    center: np.ndarray      # shape (3,)
    center_offset: np.ndarray  # shape (3,)
    vertices: np.ndarray  # shape (8, 3)

def loadMesh(path: str) -> trimesh.Geometry:
    return trimesh.load(path, force='mesh')

def createDims(bb: BoundingBox) -> WorldDims:
    size = np.round(bb.size / 25).astype(int)
    size = np.maximum(size, 1)  # clamp each dim to at least 1
    volume = np.prod(size)
    
    return WorldDims(size=size, vol=volume)

def createBoundingBox(mesh: trimesh.Geometry) -> BoundingBox:
    verts = mesh.vertices
    min_corner = verts.min(axis=0)
    max_corner = verts.max(axis=0)
    size = max_corner - min_corner
    center = (min_corner + max_corner) / 2

    center_offset = -center
    center_offset[2] = -min_corner[2]

    corners = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
    ], dtype=float)
    bbox_vertices = min_corner + corners * (max_corner - min_corner)
    bbox_vertices += center_offset

    return BoundingBox(min_corner, max_corner, size, center, center_offset, bbox_vertices)

def reduceMesh(mesh: trimesh.Geometry, max_faces: int) -> trimesh.Geometry:
    current_faces = mesh.faces.shape[0]
    if current_faces > max_faces:
        reduction_fraction = 1 - (max_faces / current_faces)
        mesh = mesh.simplify_quadric_decimation(reduction_fraction)
    return mesh
