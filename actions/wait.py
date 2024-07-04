from actions.action import Action
from time import sleep
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox


class Wait(Action):

    def __init__(self, wait_time=None):
        if wait_time is None:
            while True:
                wait_time = input("How long would you like to wait for (in seconds)? ")
                try:
                    wait_time = float(wait_time)
                    if wait_time >= 0:
                        break
                except ValueError:
                    pass
        self.wait_time = wait_time

    def __str__(self):
        return "Waiting for " + str(self.wait_time) + " seconds"

    def run(self):
        sleep(self.wait_time)

class wait_ui(QtWidgets.QWidget):
    def __init__(self, main_app, parent=None):
        super(wait_ui, self).__init__(parent)
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)  # Main layout for the configuration view

        self.label = QLabel("Create a new wait action")
        self.layout.addWidget(self.label)

        # Instructions label
        self.label = QLabel("Input the wait time:")
        self.layout.addWidget(self.label)

        # QLineEdit for how long the wait is
        self.text_input = QLineEdit()
        self.layout.addWidget(self.text_input)

        # QComboBox for where the wait should be inserted
        self.between_all = QComboBox()
        self.between_all.addItem("Only add a wait here")
        self.between_all.addItem("Add a wait between all non-wait actions")
        self.layout.addWidget(self.between_all)

        # Save button + logic
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_action)
        self.layout.addWidget(self.save_button)

        # Back button + logic
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.main_app.switch_to_main_view)
        self.layout.addWidget(self.back_button)

        self.wait_time = None

    def save_action(self):
        # Capture the text from the QLineEdit
        wait_time_str = self.text_input.text()
        try:
            wait_time = float(wait_time_str)
            if wait_time >= 0:
                wait = Wait(wait_time)
                if self.between_all.currentText() == "Only add a wait here":
                    self.main_app.add_action(wait)
                else:
                    self.main_app.add_wait_between_all(wait)
                self.main_app.switch_to_main_view()  # Switch back to the main view
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "Wait time must be a positive number.")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter a number as the wait time.")
