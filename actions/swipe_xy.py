from actions.action import Action
from MouseShortcuts import move_between, check_valid_input
from Listener import wait_for_shift_press
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton
from pynput.mouse import Controller


class SwipeXY(Action):
    def __init__(self, start = None, end = None):
        if start is None or end is None:
            print("Move your mouse to the desired start position. Press shift when ready.", end="")
            wait_for_shift_press()
            self.start = (Controller().position[0], Controller().position[1])
            print("\nMove your mouse to the desired end position. Press shift when ready.", end="")
            wait_for_shift_press()
            self.end = (Controller().position[0], Controller().position[1])
            print()  # Clearing the end="" from above
        else:

            self.start = check_valid_input(start)
            self.end = check_valid_input(end)

    def run(self):
        move_between(self.start, self.end)

    def __str__(self):
        return ("Swipe between (" + str(self.start[0]) + ", " + str(self.start[1]) + ") and (" + str(self.end[0]) +
            ", " + str(self.end[1]) + ")")


class SwipeXyUi(QtWidgets.QWidget):  # Using Ui not UI, as XYUI is unclear
    def __init__(self, main_app, parent=None):
        super(SwipeXyUi, self).__init__(parent)
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Make a new swipe action")
        self.layout.addWidget(self.label)

        self.initial_coordinates_label = QLabel("Press shift to set the initial coordinates to where your mouse is.")
        self.layout.addWidget(self.initial_coordinates_label)

        self.initial_coordinates_display = QLabel("Initial coordinates: Not set")
        self.layout.addWidget(self.initial_coordinates_display)

        self.final_coordinates_label = QLabel("Press control to set the final coordinates to where your mouse is.")
        self.layout.addWidget(self.final_coordinates_label)

        self.final_coordinates_display = QLabel("Final coordinates: Not set")
        self.layout.addWidget(self.final_coordinates_display)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_action)
        self.layout.addWidget(self.save_button)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.main_app.switch_to_main_view)
        self.layout.addWidget(self.back_button)

        self.initial_coordinates = None
        self.final_coordinates = None
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Shift:
            self.initial_coordinates = Controller().position
            self.initial_coordinates_display.setText("Coordinates: " + str(self.initial_coordinates))
            return True
        elif event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Control:
            self.final_coordinates = Controller().position
            self.final_coordinates_display.setText("Coordinates: " + str(self.final_coordinates))
            return True
        return super(SwipeXyUi, self).eventFilter(obj, event)

    def save_action(self):
        # Save the action
        initial_coordinates = self.initial_coordinates
        final_coordinates = self.final_coordinates
        if initial_coordinates and final_coordinates:
            action = SwipeXY(initial_coordinates, final_coordinates)
            self.main_app.add_action(action)
        self.main_app.switch_to_main_view()
