from actions.action import Action
from actions.mouse_shortcuts import move_between, check_valid_input
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton
from PyQt6 import QtCore, QtWidgets
from pynput.mouse import Controller

# Windows has DPI scaling issues, so if on Windows these global flags need to be set. if os.name == 'nt'
# should check for Windows and only be True there, but as windll doesn't exist anywhere else, the
# except AttributeError is there for safety. See https://pypi.org/project/pynput/
import os
try:
    if os.name == 'nt':
        import ctypes
        PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
except AttributeError:
    pass


class SwipeXY(Action):
    def __init__(self, start, end):
        """
        Sets initial and final coordinates for the swipe action. Must be in the form [x, y] or (x, y). If one
        or both are valid, it will be set to (0, 0) instead
        :param start: A list in the form [int(x), int(y)]. Where the mouse should start
        :param end: A list in the form [int(x), int(y)]. Where the mouse should end
        """
        self.start = check_valid_input(start)
        self.end = check_valid_input(end)

    def run(self):
        """
        Swipes the mouse between the start and end positions, with left click held down
        """
        move_between(self.start, self.end)

    def __str__(self):
        """
        Returns a string representation of SwipeXY in the form "Swipe between (x1, y1) and (x2, y2)"
        """
        return ("Swipe between (" + str(self.start[0]) + ", " + str(self.start[1]) + ") and (" + str(self.end[0]) +
                ", " + str(self.end[1]) + ")")

    def update_fields(self, start, end):
        """
        Sets new start and end fields
        :param start: A list in the form [int(x), int(y)]. Where the mouse should start
        :param end: A list in the form [int(x), int(y)]. Where the mouse should end
        """
        self.__init__(start, end)


class SwipeXyUI(QtWidgets.QWidget):
    def __init__(self, main_app, swipe_xy_to_edit=None):
        """
        Establishes the main application frame, and calls init_ui to do the rest
        :param main_app: The application that this is being called from
        :param swipe_xy_to_edit: The passed in SwipeXY action to be edited. Defaults to None
        """
        super(SwipeXyUI, self).__init__()

        if swipe_xy_to_edit is not None:
            self.initial_coordinates = swipe_xy_to_edit.start
            self.final_coordinates = swipe_xy_to_edit.end
        else:
            self.initial_coordinates = None
            self.final_coordinates = None
        self.main_app = main_app
        self.init_ui(swipe_xy_to_edit)

    def init_ui(self, swipe_xy_to_edit=None):
        """
        Initializes the UI elements and installs a custom event filter to listen for keystrokes
        :param swipe_xy_to_edit: The passed in SwipeXY action to be edited. Defaults to None
        """
        layout = QVBoxLayout(self)
        label = QLabel("Make a new swipe action")
        layout.addWidget(label)

        initial_coordinates_label = QLabel("Press shift to set the initial coordinates to where your mouse is.")
        layout.addWidget(initial_coordinates_label)

        self.initial_coordinates_display = QLabel("Initial coordinates: Not set")
        layout.addWidget(self.initial_coordinates_display)

        final_coordinates_label = QLabel("Press control to set the final coordinates to where your mouse is.")
        layout.addWidget(final_coordinates_label)

        self.final_coordinates_display = QLabel("Final coordinates: Not set")
        layout.addWidget(self.final_coordinates_display)

        if swipe_xy_to_edit is not None:
            self.initial_coordinates_display.setText("Coordinates: " + str(self.initial_coordinates))
            self.final_coordinates_display.setText("Coordinates: " + str(self.final_coordinates))

        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_action(swipe_xy_to_edit))
        layout.addWidget(save_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.main_app.switch_to_main_view)
        layout.addWidget(back_button)

        self.installEventFilter(self)

    def eventFilter(self, source, event):
        """
        :param source: The source of the event - not used, only present as it is a set field
        :param event: The thing that happened to the UI
        :return: True if one of the custom events has been fulfilled. Otherwise, defaults to the default eventFilter
            PyQt5 logic
        """
        if event.type() == QtCore.QEvent.Type.KeyPress and event.key() == QtCore.Qt.Key.Key_Shift:
            self.initial_coordinates = Controller().position
            self.initial_coordinates_display.setText("Coordinates: " + str(self.initial_coordinates))
            return True
        elif event.type() == QtCore.QEvent.Type.KeyPress and event.key() == QtCore.Qt.Key.Key_Control:
            self.final_coordinates = Controller().position
            self.final_coordinates_display.setText("Coordinates: " + str(self.final_coordinates))
            return True
        return super(SwipeXyUI, self).eventFilter(source, event)

    def save_action(self, swipe_xy_to_edit):
        """
        Saves the SwipeXY, as long as the user has given initial and final coordinates. Otherwise, it
        returns to the main screen, saving nothing. This can be used to edit a SwipeXY if one is passed
        in, or create a new one and return it to the parent app's action list
        """
        initial_coordinates = self.initial_coordinates
        final_coordinates = self.final_coordinates
        if initial_coordinates and final_coordinates:
            if swipe_xy_to_edit:
                swipe_xy_to_edit.update_fields(initial_coordinates, final_coordinates)
                self.main_app.update_action_list()
            else:
                action = SwipeXY(initial_coordinates, final_coordinates)
                self.main_app.add_action(action)
        self.main_app.switch_to_main_view()
