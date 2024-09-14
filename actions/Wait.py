from actions.action import Action
from time import sleep
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit


class Wait(Action):
    """
    # The Wait action. When called, it causes the thread to sleep for an amount of time specified
    at the creation of the object. This implements the Action class
    """

    def __init__(self, wait_time):
        """
        Creates a variable and sets it equal to the passed in wait_time. If this isn't a float greater than or
        equal to zero, the var is instead set to zero
        :param wait_time: float, the amount of time that should be elapsed before the next Action can happen
        """
        if not check_number_validity(wait_time):
            wait_time = 0
        self.wait_time = wait_time

    def __str__(self):
        """
        Returns a string representation of the Wait object in the form "Waiting for [x] seconds"
        """
        return "Waiting for " + str(self.wait_time) + " seconds"

    def run(self):
        """
        Makes the thread sleep for as long as wait_time specifies
        """
        sleep(self.wait_time)

    def update_fields(self, wait_time):
        """
        Updates the Wait Action to have a new time to wait
        :param wait_time: float, the amount of time that should be elapsed before the next Action can happen
        """
        self.__init__(wait_time)


def check_number_validity(wait_time):
    """
    Checks that the passed in value is a float greater than or equal to zero. Returns True if so, False otherwise
    :param wait_time: The String / float to be checked
    :return: True if the number is greater than or equal to zero, False otherwise
    """
    try:
        wait_time = float(wait_time)
        if wait_time >= 0:
            return True
    except ValueError:
        return False


class WaitUI(QtWidgets.QWidget):
    def __init__(self, main_app, wait_to_edit=None):
        """
        Establishes the main application frame, and calls init_ui to do the rest
        :param main_app: The application that this is being called from
        :param wait_to_edit: The passed in Wait action to be edited. Defaults to None
        """
        super(WaitUI, self).__init__()
        self.main_app = main_app
        self.init_ui(wait_to_edit)

    def init_ui(self, wait_to_edit=None):
        """
        Initializes the UI elements
        """
        layout = QVBoxLayout(self)

        self.title = QLabel("Create a new wait action")
        layout.addWidget(self.title)

        self.prompt = QLabel("Input the wait time:")
        layout.addWidget(self.prompt)

        self.text_input = QLineEdit()
        layout.addWidget(self.text_input)

        if wait_to_edit is not None:
            self.text_input.setText(str(wait_to_edit.wait_time))
            self.title.setText("Edit wait action")
        else:
            self.between_all = QComboBox()
            self.between_all.addItem("Only add a wait here")
            self.between_all.addItem("Add a wait between all non-wait actions")
            layout.addWidget(self.between_all)

        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_action(wait_to_edit))
        layout.addWidget(save_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.main_app.switch_to_main_view)
        layout.addWidget(back_button)

    def save_action(self, wait_to_edit):
        """
        Checks to see that the user has inputted a time in text_input which is a float that's greater than
        or equal to zero. If this fails a popup opens telling the user to input a positive number, and
        a Wait object is created with the wait time and returned to UI3
        If between_all is set to only add a wait here, one wait is added to the end of UI3's action list. Otherwise,
        a wait is added between all non-Wait actions
        :return: an instance of Wait to UI3 with specifications for if it should be added between all non-Wait
        actions or just added at the end
        """
        wait_time_str = self.text_input.text()
        if check_number_validity(wait_time_str):
            wait = Wait(float(wait_time_str))
            if (hasattr(self, 'between_all')
                    and self.between_all.currentText() == "Add a wait between all non-wait actions"):
                self.main_app.add_wait_between_all(wait)
            else:
                if wait_to_edit:
                    wait_to_edit.update_fields(float(wait_time_str))
                else:
                    self.main_app.add_action(wait)
            self.main_app.update_action_list()
            self.main_app.switch_to_main_view()
        else:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Wait time must be a positive number.")
