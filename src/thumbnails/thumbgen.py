import numpy as np
import trimesh
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QImage, QPainter, QPixmap, QPolygonF


def make_thumbnail(mesh: trimesh.Trimesh, size=64) -> QPixmap:
    """
    Create a 2D isometric thumbnail of a trimesh.Trimesh.

    Parameters:
    - mesh: a trimesh.Trimesh instance
    - size: output pixmap width/height in pixels
    """
    # fixed isometric angles
    ang_z, ang_x = -45, 35.264
    Rz = np.array([
        [ np.cos(np.radians(ang_z)), -np.sin(np.radians(ang_z)), 0 ],
        [ np.sin(np.radians(ang_z)),  np.cos(np.radians(ang_z)), 0 ],
        [ 0,                          0,                          1 ]
    ])
    Rx = np.array([
        [1, 0,                           0],
        [0, np.cos(np.radians(ang_x)), -np.sin(np.radians(ang_x))],
        [0, np.sin(np.radians(ang_x)),  np.cos(np.radians(ang_x))]
    ])
    R = Rx @ Rz

    # get triangles [n_faces, 3,3] and normals [n_faces,3]
    tris = mesh.vertices[mesh.faces]         # (F,3,3)
    norms = mesh.face_normals                # (F,3)

    # rotate all verts & normals
    tris_rot = tris @ R.T                    # (F,3,3)
    norms_rot = norms @ R.T                  # (F,3)

    # flatten for bounding box
    pts = tris_rot.reshape(-1, 3)
    xs, ys = pts[:,0], pts[:,1]
    minx, maxx = xs.min(), xs.max()
    miny, maxy = ys.min(), ys.max()
    spanx = maxx - minx or 1e-6
    spany = maxy - miny or 1e-6

    # prepare image
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    painter = QPainter(img)
    painter.setPen(Qt.NoPen)

    # simple shading
    light = np.array([0.3,0.5,0.8])
    light /= np.linalg.norm(light)

    # draw each triangle
    for n, tri in zip(norms_rot, tris_rot):
        brightness = max(0.0, float(np.dot(n, light)))
        val = int(150 * brightness + 50)
        color = QColor(val, val, val, 200)
        painter.setBrush(color)

        poly = QPolygonF()
        for vx, vy, vz in tri:
            # project & normalize into [2, size-2]
            nx = (vx - minx) / spanx * (size - 4) + 2
            ny = (vy - miny) / spany * (size - 4) + 2
            poly.append(QPointF(nx, ny))
        painter.drawPolygon(poly)

    painter.end()
    return QPixmap.fromImage(img)
