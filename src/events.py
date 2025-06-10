from PyQt5.QtCore import QEvent, QObject, pyqtSignal, QTime

class KeyFilter(QObject):
    def __init__(self):
        super().__init__()
        self._last_key = None
        self._last_time = QTime()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            now = QTime.currentTime()

            # Ignore if same key pressed within 100 ms and not autorepeat
            if (
                self._last_key == key
                and self._last_time.msecsTo(now) < 100
                and not event.isAutoRepeat()
            ):
                return False

            self._last_key = key
            self._last_time = now

            event_bus.keyPressed.emit(key)
        return False

class EventBus(QObject):
    keyPressed = pyqtSignal(int)
    tilesChanged = pyqtSignal()

event_bus = EventBus()
