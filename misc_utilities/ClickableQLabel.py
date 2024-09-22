from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import pyqtSignal, Qt, QPoint
from PyQt6.QtGui import QMouseEvent
from pynput.mouse import Controller

callback = None


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, callback_script, parent=None):
        """
        Initializes the QLabel, sets a callback script equal to the input
        :param callback_script: The script that should be run when the callback is called
        :param parent: The parent app of the label
        """
        super().__init__(parent)
        global callback
        callback = callback_script

    def mousePressEvent(self, event: QMouseEvent):
        """
        Calls the callback function with the x, y coordinates of the mouse if the label is right clicked
        :param event: The mouse click
        """
        if event.button() == Qt.MouseButton.RightButton:
            callback(QPoint(Controller().position[0], Controller().position[1]), self)
