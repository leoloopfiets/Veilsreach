import trimesh
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtGui import QIcon

from .meshlogic import BoundingBox, WorldDims

class TileData:
    def __init__(self, filepath: str, name: str, mesh: trimesh.Geometry, bb: BoundingBox, dims: WorldDims, icon: QIcon):
        self.filepath: str = filepath
        self.name: str = name
        self.mesh: trimesh.Geometry = mesh
        self.bb: BoundingBox = bb
        self.dims: WorldDims = dims
        self.icon: QIcon = icon
        self.list_id: int = None

        self._regGl()

    def dispose(self) -> None:
        if self.list_id:
            glDeleteLists(self.list_id, 1)
            self.list_id = None

    def _regGl(self) -> None:
        # Extract vertices and faces from (possibly simplified) mesh
        verts = self.mesh.vertices
        faces = self.mesh.faces
        normals = self.mesh.face_normals  # one normal per face

        # Create an OpenGL display list
        list_id = glGenLists(1)
        glNewList(list_id, GL_COMPILE)
        glPushMatrix()

        # Apply precomputed centering translation
        glTranslatef(*self.bb.center_offset)

        # Draw triangles
        glBegin(GL_TRIANGLES)
        for normal, face in zip(normals, faces):
            glNormal3fv(normal)
            for idx in face:
                glVertex3fv(verts[idx])
        glEnd()

        glPopMatrix()
        glEndList()

        self.list_id = list_id