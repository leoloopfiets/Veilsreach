import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QVector3D
from PyQt5.QtWidgets import QOpenGLWidget

from ..events import event_bus
from ..world.world import World

class WorldWidget(QOpenGLWidget):
    def __init__(self, world: World, parent=None):
        super().__init__(parent)
        
        # widget properties
        self.setMouseTracking(True)

        # common
        self.world = world
        
        # cursor
        self.resetCursor()

        # caching matrices
        self._viewport = None
        self._proj     = None
        self._mv       = None

        # listeners
        event_bus.keyPressed.connect(self._onGlobalKeyPress)

    def resetCursor(self):
        self.cursor_pos = None
        self.cursor_rotation = 0
        self.cursor_good = False
        self.cursor_mode = None   # 'pan' or 'orbit'
        self.last_mouse = None

    def _onGlobalKeyPress(self, key):
        if key == Qt.Key_R:
            self.cursor_rotation = (self.cursor_rotation + 90) % 360
            self.update()
    
    def _updateCursorPosition(self, cursor_x, cursor_y):
        vp, proj, mv = self._viewport, self._proj, self._mv
        real_y = vp[3] - cursor_y
        x0,y0,z0 = gluUnProject(cursor_x, real_y, 0.0, mv, proj, vp)
        x1,y1,z1 = gluUnProject(cursor_x, real_y, 1.0, mv, proj, vp)
        t = -z0 / (z1 - z0)
        wx = x0 + t*(x1 - x0)
        wy = y0 + t*(y1 - y0)
        wz = 0.0

        self.cursor_pos = [wx, wy, wz]
    
    def _updateMatrices(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        phi = np.radians(self.world.camera.elev)
        th  = np.radians(self.world.camera.azim)
        cx = self.world.camera.pan.x() + self.world.camera.dist * np.cos(phi) * np.cos(th)
        cy = self.world.camera.pan.y() + self.world.camera.dist * np.cos(phi) * np.sin(th)
        cz =                  self.world.camera.dist * np.sin(phi)
        gluLookAt(cx, cy, cz,
                  self.world.camera.pan.x(), self.world.camera.pan.y(), 0.0,
                  0, 0, 1)

        # cache matrices and viewport
        self._viewport = glGetIntegerv(GL_VIEWPORT)
        self._proj     = glGetDoublev(GL_PROJECTION_MATRIX)
        self._mv       = glGetDoublev(GL_MODELVIEW_MATRIX)

    # Override
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.2,0.2,0.2,1.0)

        # lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [0.5,1.0,0.8,0.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.3,0.3,0.3,1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.7,0.7,0.7,1.0])

        # grid on Z=0 (XY-plane)
        self.grid_list = glGenLists(1)
        glNewList(self.grid_list, GL_COMPILE)
        glDisable(GL_LIGHTING)
        glColor3f(0.3,0.3,0.3)
        glBegin(GL_LINES)
        gridSize = 100
        gridSquareSize = 1
        for i in range(-gridSquareSize * gridSize, gridSquareSize * gridSize + 1, gridSquareSize):
            # horizontal lines
            glVertex3f(-gridSquareSize * gridSize, i, 0); glVertex3f(gridSquareSize * gridSize, i, 0)
            # vertical lines
            glVertex3f(i, -gridSquareSize * gridSize, 0); glVertex3f(i, gridSquareSize * gridSize, 0)
        glEnd()
        glEnable(GL_LIGHTING)
        glEndList()

    # Override
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/max(h,1), 0.1, 2000.0)
        glMatrixMode(GL_MODELVIEW)

    # Override
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._updateMatrices()

        # draw grid
        if self.world.grid_shown:
            glPushMatrix()
            glScalef(1.0 * self.world.grid_size, 1.0 * self.world.grid_size, 1)
            glCallList(self.grid_list)
            glPopMatrix()

        # draw world objects
        glColor3f(0.5,0.5,0.5)
        for obj in self.world.objects:
            glPushMatrix()
            x, y, z = obj.pos
            mesh = self.world.tile_meshes[obj.mesh_id]
            glTranslatef(x, y, z)
            glRotatef(obj.rotation, 0, 0, 1)
            glTranslatef(mesh.bb.size[0] / 2, mesh.bb.size[1] / 2, 0)
            glCallList(mesh.list_id)
            glPopMatrix()

        # draw world object roots
        glDisable(GL_LIGHTING)
        glColor3f(0.2, 1, 1)
        for obj in self.world.objects:
            glPushMatrix()
            x, y, z = obj.pos
            glTranslatef(x, y, z)
            glBegin(GL_QUADS)
            size = 5
            glVertex3f(-size/2, -size/2, -0.1)
            glVertex3f(size/2, -size/2, -0.1)
            glVertex3f(size/2, size/2, -0.1)
            glVertex3f(-size/2, size/2, -0.1)
            glEnd()
            glPopMatrix()
        glEnable(GL_LIGHTING)

        if self.cursor_pos is not None:
            glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT | GL_DEPTH_BUFFER_BIT)
            glEnable(GL_BLEND)
            glDisable(GL_DEPTH_TEST)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDisable(GL_LIGHTING)

            gx, gy, gz = self.world.toGrid(self.cursor_pos)
            h_cell = self.world.grid_size / 2

            glPushMatrix()
            glTranslatef(gx, gy, gz)

            # draw cursor
            if self.world.selected_mesh is not None:
                # draw mesh cursor
                ghost_tile = self.world.tile_meshes[self.world.selected_mesh]
                # ox, oy, oz = self.world.toGridObject(ghost_tile.bb.size, rotation=round(self.cursor_rotation / 90))
                # glTranslatef(-ox, -oy, 0)
                glRotatef(self.cursor_rotation, 0, 0, 1)
                glTranslatef(ghost_tile.bb.size[0] / 2, ghost_tile.bb.size[1] / 2, 0)

                # draw ghost mesh
                glColor4f(1, 1, 1, 0.4)
                glCallList(ghost_tile.list_id)

                # draw bounding box
                glColor4f(0, 1, 0, 0.8) if self.cursor_good else glColor4f(1, 0, 0, 0.8)
                corners = ghost_tile.bb.vertices
                edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]

                glBegin(GL_LINES)
                for a, b in edges:
                    glVertex3f(*corners[a])
                    glVertex3f(*corners[b])
                glEnd()

                # draw dims box
                # half = ghost_tile.dims.size / 2 * 25
                # z = -0.0001
                # corners = [
                #     (-half[0], -half[1], z),
                #     ( half[0], -half[1], z),
                #     ( half[0],  half[1], z),
                #     (-half[0],  half[1], z),
                # ]
                # glColor4f(0, 0, 1, 0.5)  # greenish, semi-transparent

                # glBegin(GL_QUADS)
                # for x, y, z in corners:
                #     glVertex3f(x, y, z)
                # glEnd()


            else:
                # draw empty cursor
                glColor4f(1, 1, 1, 0.3)
                glTranslatef(h_cell, h_cell, h_cell)
                glRotatef(self.cursor_rotation, 0, 0, 1)
                glTranslatef(-h_cell, -h_cell, -h_cell)
                size = self.world.grid_size

                glBegin(GL_LINE_LOOP)
                glVertex3f(0, 0, 0)
                glVertex3f(size, 0, 0)
                glVertex3f(size, size, 0)
                glVertex3f(0, size, 0)
                glEnd()
                
                # draw corner triangle
                glColor4f(1, 1, 1, 0.3)
                glBegin(GL_TRIANGLES)
                glVertex3f(0, 0, 0)
                glVertex3f(4.0, 0, 0)
                glVertex3f(0, 4.0, 0)
                glEnd()

            glPopMatrix()
            glEnable(GL_LIGHTING)
            glPopAttrib()

    # Override
    def mousePressEvent(self, ev):
        self.last_mouse = ev.pos()
        if ev.button() == Qt.LeftButton:
            if not self.cursor_pos:
                return
            if self.world.delete_mode:
                # compute grid cell under cursor
                grid_pos = self.world.toGrid(self.cursor_pos)
                # remove the first object found at that cell
                for obj in list(self.world.objects):
                    if obj.pos == grid_pos:
                        self.world.objects.remove(obj)
                        break
                self.update()
            else:
                self.world.placeObject(self.cursor_pos, self.cursor_rotation)
                self.update()
        elif ev.button() == Qt.MiddleButton:
            self.cursor_mode = 'orbit'
        elif ev.button() == Qt.RightButton:
            self.cursor_mode = 'pan'

    # Override
    def mouseReleaseEvent(self, ev):
        self.cursor_mode = None

    # Override
    def mouseMoveEvent(self, ev):
        dx = ev.x() - (self.last_mouse.x() if self.last_mouse else ev.x())
        dy = ev.y() - (self.last_mouse.y() if self.last_mouse else ev.y())

        if self.cursor_mode == 'pan':
            # calculate camera axes
            phi = np.radians(self.world.camera.elev)
            th = np.radians(self.world.camera.azim)
            forward = np.array([np.cos(phi)*np.cos(th),
                                np.cos(phi)*np.sin(th),
                                np.sin(phi)])
            right = np.cross(forward, [0,0,1])
            right /= np.linalg.norm(right)
            # compute true up in world XY-plane
            up = np.cross(right, forward)
            up /= np.linalg.norm(up)
            factor = self.world.camera.dist / 500.0 * 0.5
            d = (dx * right[:2] + dy * up[:2]) * factor
            self.world.camera.pan += QVector3D(d[0], d[1], 0)

        elif self.cursor_mode == 'orbit':
            self.world.camera.azim += dx * 0.3
            self.world.camera.elev = max(-89, min(89, self.world.camera.elev + dy * 0.3))
        
        self._updateCursorPosition(ev.x(), ev.y())
        self.last_mouse = ev.pos()
        self.update()

    # Override
    def leaveEvent(self, ev):
        super().leaveEvent(ev)
        self.resetCursor()
        self.update()

    # Override
    def wheelEvent(self, ev):
        self.world.camera.dist *= 0.9 if ev.angleDelta().y() > 0 else 1.1

        self.makeCurrent() # Force enable GL context
        self._updateMatrices()
        self._updateCursorPosition(ev.x(), ev.y())
        self.update()
