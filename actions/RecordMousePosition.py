from pynput.mouse import Controller
from actions.action import Action

from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton
from PyQt6 import QtWidgets

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


class RecordMousePosition(Action):
    """
    Implements Action. An object that when run will record the mouse's current position
    """

    def __init__(self):
        """
        Creates a coordinates variable set to None
        """
        self.coordinates = None

    def run(self):
        """
        If coordinates are present, it moves the mouse to the recorded position and removes them. Otherwise, records
        new coordinates
        """
        if self.coordinates:
            Controller().position = self.coordinates
            self.coordinates = None
        else:
            self.coordinates = Controller().position

    def __str__(self):
        """
        Returns "Recording mouse position / moving mouse"
        """
        return "Recording mouse position / moving to said position"

    def clear_coordinates(self):
        self.coordinates = None


class RecordMousePositionUI(QtWidgets.QWidget):
    """
    Basic UI to alert the user what RecordMousePosition does, allows them to create one or not
    """
    def __init__(self, main_app, action_list):
        """
        Alerts the user to what RecordMousePosition does. If the passed in action_list already has a RecordMousePosition
        in it, then it'll pass a copy of that RecordMousePosition back to the main app
        :param main_app: The PyQt6 application that called this
        "param action_list" A list of Action objects
        """
        super(RecordMousePositionUI, self).__init__()
        self.main_app = main_app

        layout = QVBoxLayout(self)
        label = QLabel("Run this once to record the mouse's position, "
                       "run it again to move the mouse to the recorded position")
        layout.addWidget(label)

        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_action(action_list))
        layout.addWidget(save_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.main_app.switch_to_main_view)
        layout.addWidget(back_button)

    def save_action(self, action_list):
        """
        Creates a new action if no RecordMousePosition already exists in action_list and returns it, otherwise
        creates a new one and returns that to main_app
        :param action_list: The list of Action objects
        """
        return_action = None
        for action in action_list:
            if type(action) is RecordMousePosition:
                return_action = action
                break
        if return_action is None:
            return_action = RecordMousePosition()

        self.main_app.add_action(return_action)
        self.main_app.switch_to_main_view()
