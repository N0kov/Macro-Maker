from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit
from pynput.mouse import Button, Controller
from .action import Action
from MouseShortcuts import click_pos, check_valid_input


class ClickX(Action):
    def __init__(self, coordinates=None, click_type=None):
        if coordinates is None:
            self.coordinates = (0, 0)
        else:
            self.coordinates = check_valid_input(coordinates)

        self.click = "Left"
        self.click_type = Button.left
        if click_type in ("r", "right"):
            self.click_type = Button.right
            self.click = "Right"
        elif click_type in ("m", "middle"):
            self.click_type = Button.middle
            self.click = "Middle"

    def run(self):
        click_pos(self.coordinates, self.click_type)

    def __str__(self):
        return self.click + " click at " + str(self.coordinates)


class ClickXUI(QtWidgets.QWidget):
    def __init__(self, main_app, parent=None):
        super(ClickXUI, self).__init__(parent)
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Make a new click action")
        self.layout.addWidget(self.label)

        self.click_type_label = QLabel("Select Click Type:")
        self.layout.addWidget(self.click_type_label)
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(["Left", "Right", "Middle"])
        self.layout.addWidget(self.click_type_combo)

        self.coordinates_label = QLabel("Press shift to set coordinates to where your mouse is.")
        self.layout.addWidget(self.coordinates_label)

        self.coordinates_display = QLabel("Coordinates: Not set")
        self.layout.addWidget(self.coordinates_display)

        self.index = QLineEdit()
        self.layout.addWidget(self.index)

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
        return super(ClickXUI, self).eventFilter(obj, event)

    def set_coordinates(self):
        self.coordinates = Controller().position
        self.coordinates_display.setText("Coordinates: " + str(self.coordinates))

    def save_action(self):
        click_type = self.click_type_combo.currentText().lower()[0]
        coordinates = self.coordinates
        if coordinates:
            action = ClickX(coordinates, click_type)
            self.main_app.add_action(action)
        self.main_app.switch_to_main_view()
