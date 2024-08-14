from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import pyqtSignal, Qt, QPoint
from PyQt6.QtGui import QMouseEvent
from pynput.mouse import Controller

callback = None


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, callback_script, parent=None):
        super().__init__(parent)
        global callback
        callback = callback_script

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            callback(QPoint(Controller().position[0], Controller().position[1]), self)
