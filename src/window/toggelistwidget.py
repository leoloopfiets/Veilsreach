from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QListWidget

from ..events import event_bus

class ToggleListWidget(QListWidget):
    selected = pyqtSignal(int)    # emits selected row
    deselected = pyqtSignal()     # emits when cleared/deselected

    def __init__(self, parent=None):
        super().__init__(parent)

        event_bus.keyPressed.connect(self._onGlobalKeyPress)

    def clearSelectionWithSignal(self):
        super().clearSelection()
        self.setCurrentRow(-1)  # force row deselection
        self.deselected.emit()

    def _onGlobalKeyPress(self, key):
        if key == Qt.Key_Escape:
            if self.currentRow() != -1:
                self.clearSelectionWithSignal()
                return

    # Override
    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item is not None:
            row = self.row(item)
            if self.currentRow() == row:
                self.clearSelectionWithSignal()
                return
            else:
                super().mousePressEvent(event)
                self.selected.emit(row)
                return
        super().mousePressEvent(event)
