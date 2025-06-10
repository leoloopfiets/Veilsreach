from PyQt5.QtGui import QVector3D

class WorldCamera():
    def __init__(self):
        self.pan   = QVector3D(0,0,0)
        self.dist  = 500.0
        self.azim  = 45.0
        self.elev  = 30.0

    def to_dict(self) -> dict:
        return {
            "pan": [self.pan.x(), self.pan.y(), self.pan.z()],
            "dist": self.dist,
            "azim": self.azim,
            "elev": self.elev
        }

    @staticmethod
    def from_dict(data: dict) -> "WorldCamera":
        obj = WorldCamera()
        obj.pan = QVector3D(*data["pan"])
        obj.dist = data["dist"]
        obj.azim = data["azim"]
        obj.elev = data["elev"]
        return obj

