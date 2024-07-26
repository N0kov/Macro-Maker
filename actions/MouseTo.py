from mouse_shortcuts import check_valid_input
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton
from PyQt6 import QtCore, QtWidgets
from pynput.mouse import Controller
from actions.action import Action

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


class MouseTo(Action):
    """
    Implements Action. An object that holds [x, y] coordinates. Can be run to move the mouse to said coordinates
    """

    def __init__(self, coordinates):
        """
        Checks coordinates for if it is a list / tuple that has two ints / floats in it. If not, self.coordinates
        is set to [0, 0], otherwise it's set as a list with coordinate's preexisting values
        """
        self.coordinates = check_valid_input(coordinates)

    def run(self):
        """
        Moves the mouse to the position specified in self.coordinates
        """
        Controller().position = (self.coordinates[0], self.coordinates[1])

    def __str__(self):
        """
        Returns a string representation of the MosueTo event in the form "[click type] click at (x, y)"
        """
        return "Mouse to (" + str(self.coordinates[0]) + ", " + str(self.coordinates[1]) + ")"


class MouseToUI(QtWidgets.QWidget):
    """
    MouseTo's UI. This allows the user to set a position on the screen that they want to move the mouse to and
    save it as a MouseTo object.
    """

    def __init__(self, main_app, mouse_to_to_edit=None):
        """
        Establishes the main application frame, and calls init_ui to do the rest
        :param main_app: The application that this is being called from
        :param mouse_to_to_edit: The passed in MouseTo action to be edited. Defaults to None
        """
        super(MouseToUI, self).__init__()
        if mouse_to_to_edit is not None:
            self.coordinates = mouse_to_to_edit.coordinates
        else:
            self.coordinates = None
        self.main_app = main_app
        self.init_ui(mouse_to_to_edit)

    def init_ui(self, mouse_to_to_edit=None):
        """
        Initializes the UI elements and installs a custom event filter to listen for keystrokes
        :param mouse_to_to_edit: The passed in MouseTo action to be edited. Defaults to None
        """
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Make a mouse movement action")
        self.layout.addWidget(self.label)

        self.coordinates_label = QLabel("Press shift to set coordinates to where your mouse is.")
        self.layout.addWidget(self.coordinates_label)

        self.coordinates_display = QLabel("Coordinates: Not set")
        self.layout.addWidget(self.coordinates_display)

        if mouse_to_to_edit is not None:
            self.coordinates_display.setText("Coordinates: " + str(self.coordinates))

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_action)
        self.layout.addWidget(self.save_button)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.main_app.switch_to_main_view)
        self.layout.addWidget(self.back_button)

        self.installEventFilter(self)

    def eventFilter(self, source, event):
        """
        Listens for when the user presses shift. When they do, it records the position of their mouse. Reverts to
            the default eventFilter logic otherwise
        :param source: The source of the event - not used, only present as it is a set field
        :param event: The thing that happened to the UI
        :return: True if one of the custom events has been fulfilled. Otherwise, defaults to the default eventFilter
            PyQt5 logic
        """
        if event.type() == QtCore.QEvent.Type.KeyPress and event.key() == QtCore.Qt.Key.Key_Shift:
            self.coordinates = Controller().position
            self.coordinates_display.setText("Coordinates: " + str(self.coordinates))
            return True
        return super(MouseToUI, self).eventFilter(source, event)

    def save_action(self):
        """
        If coordinates exist, this creates a MouseTo object using self.coordinates, and returns it
         to UI3's action list. If coordinates is None, nothing happens
        """
        coordinates = self.coordinates
        if coordinates:
            action = MouseTo(coordinates)
            self.main_app.add_action(action)
        self.main_app.switch_to_main_view()
