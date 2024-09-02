from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QComboBox, QPushButton
from pynput.mouse import Button, Controller
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


class ClickX(Action):
    """
    Implements Action. A class that holds pynput data of coordinates to be clicked and the type of click. Can be run to
    perform the specified click in the specified spot
    """

    def __init__(self, coordinates, click_type):
        """
        Initializes ClickX. Checks the data passed in for validity
        :param coordinates: The x, y coordinates to be clicked at. List or tuple
        :param click_type: String, the type of click. Defaults to left, but can be for right or middle
        """
        self.coordinates = coordinates

        self.click = "Left"  # The default for if the click isn't passed in correctly
        self.click_type = Button.left
        if click_type in ("r", "right"):
            self.click_type = Button.right
            self.click = "Right"
        elif click_type in ("m", "middle"):
            self.click_type = Button.middle
            self.click = "Middle"

    def run(self):
        """
        Moves the mouse to the specified coordinates in self.coordinates and performs the specified click in click_type
        Only clicks if coordinates is none
        """
        if self.coordinates:
            Controller().position = (self.coordinates[0], self.coordinates[1])
        Controller().click(self.click_type, 1)

    def __str__(self):
        """
        Returns a string representation of the ClickX object in the form "[click type] click at (x, y)"
        """
        if self.coordinates:
            return self.click + " click at (" + str(self.coordinates[0]) + ", " + str(self.coordinates[1]) + ")"
        else:
            return self.click + " clicking"

    def update_fields(self, coordinates, click_type):
        self.__init__(coordinates, click_type)


class ClickXUI(QtWidgets.QWidget):
    """
    UI for ClickX, allows the user to set a position they want to click at and what type of click they want graphically
    """

    def __init__(self, main_app, click_x_to_edit=None):
        """
        Establishes the main application frame, and calls init_ui to do the rest
        :param main_app: The application that this is being called from
        :param click_x_to_edit: The passed in Wait action to be edited. Defaults to None
        """
        super(ClickXUI, self).__init__()
        self.main_app = main_app
        if click_x_to_edit is not None:
            self.coordinates = click_x_to_edit.coordinates
        else:
            self.coordinates = None
        self.init_ui(click_x_to_edit)

    def init_ui(self, click_x_to_edit=None):
        """
        Initializes the UI elements and installs a custom event filter to listen for keystrokes
        :param click_x_to_edit: The passed in Wait action to be edited. Defaults to None
        """
        layout = QVBoxLayout(self)
        self.label = QLabel("Make a new click action")
        layout.addWidget(self.label)

        self.click_type_label = QLabel("Select Click Type:")
        layout.addWidget(self.click_type_label)
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(["Left", "Right", "Middle"])
        layout.addWidget(self.click_type_combo)

        self.coordinates_label = QLabel("Press shift to set coordinates to where your mouse is."
                                        "\n\nDon't record a position if you "
                                        "want the mouse to click where it already is.")
        layout.addWidget(self.coordinates_label)

        self.coordinates_display = QLabel("Coordinates: Not set")
        layout.addWidget(self.coordinates_display)

        if click_x_to_edit is not None:
            self.click_type_combo.setCurrentIndex(self.click_type_combo.findText(click_x_to_edit.click))
            self.coordinates_display.setText("Coordinates: " + str(self.coordinates))

        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_action(click_x_to_edit))
        layout.addWidget(save_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.main_app.switch_to_main_view)
        layout.addWidget(back_button)

        self.installEventFilter(self)

    def eventFilter(self, source, event):
        """
        Listens for when the user presses shift. When they do, it records the position of their mouse. Reverts to
            the default eventFilter logic otherwise
        :param source: The source of the event - not used, only present as it is a set field
        :param event: The thing that happened to the UI
        :return: True if one of the custom events has been fulfilled. Otherwise, defaults to the default eventFilter
            PyQt6 logic
        """
        if event.type() == QtCore.QEvent.Type.KeyPress and event.key() == QtCore.Qt.Key.Key_Shift:
            self.set_coordinates()
            return True
        return super(ClickXUI, self).eventFilter(source, event)

    def set_coordinates(self):
        """
        Records the coordinates of the mouse, and sets coordinates_display to match the new coordinates
        """
        self.coordinates = Controller().position
        self.coordinates_display.setText("Coordinates: " + str(self.coordinates))

    def save_action(self, click_x_to_edit):
        """
        Creates a ClickX object and returns it to the main app. If no coordinates have been specified, the mouse
        won't move when the action is run
        :return: A ClickX object with the coordinates and click data to UI3's action list.
        """
        click_type = self.click_type_combo.currentText().lower()[0]
        if click_x_to_edit:
            click_x_to_edit.update_fields(self.coordinates, click_type)
            self.main_app.update_action_list()
        else:
            action = ClickX(self.coordinates, click_type)
            self.main_app.add_action(action)
        self.main_app.switch_to_main_view()
