from MouseShortcuts import mouse_to, get_mouse_position
from Listener import wait_for_shift_press
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton
from pynput.mouse import Controller
from .action import Action


class MouseTo(Action):
    def __init__(self, coordinates=None):
        if coordinates is None:
            print("Move your mouse to the desired position. Press shift when ready. ", end="")
            wait_for_shift_press()
            self.coordinates = (get_mouse_position()[0], get_mouse_position()[1])
        else:
            self.coordinates = coordinates

    def run(self):
        mouse_to(self.coordinates)

    def __str__(self):
        return "Mouse to (" + str(self.coordinates[0]) + ", " + str(self.coordinates[1]) + ")"

class MouseToUI(QtWidgets.QWidget):
    def __init__(self, main_app, parent=None):
        super(MouseToUI, self).__init__(parent)
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Make a mouse movement action")
        self.layout.addWidget(self.label)

        self.coordinates_label = QLabel("Press shift to set coordinates to where your mouse is.")
        self.layout.addWidget(self.coordinates_label)

        self.coordinates_display = QLabel("Coordinates: Not set")
        self.layout.addWidget(self.coordinates_display)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_action)
        self.layout.addWidget(self.save_button)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.main_app.switch_to_main_view)
        self.layout.addWidget(self.back_button)

        self.coordinates = None
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Shift:
            self.set_coordinates()
            return True
        return super(MouseToUI, self).eventFilter(obj, event)

    def set_coordinates(self):
        # Record the mouse position
        self.coordinates = Controller().position
        self.coordinates_display.setText("Coordinates: " + str(self.coordinates))

    def save_action(self):
        # Save the action
        coordinates = self.coordinates
        if coordinates:
            action = MouseTo(coordinates)
            self.main_app.add_action(action)
        self.main_app.switch_to_main_view()
