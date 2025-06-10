from PyQt5.QtGui import QIcon, QPixmap


class IconAtlas:
    def __init__(self, path, iconWidth, iconHeight):
        self.atlas = QPixmap(path)
        self.iconWidth = iconWidth
        self.iconHeight = iconHeight

    def at(self, x, y) -> QIcon:
        return QIcon(self.atlas.copy(x * self.iconWidth, y * self.iconHeight, self.iconWidth, self.iconHeight))
