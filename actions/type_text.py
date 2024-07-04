from pynput.keyboard import Key, Controller
from actions.action import Action
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QLineEdit
import re

keyboard = Controller()


class TypeText(Action):
    def __init__(self, phrase=None):
        if phrase is None:
            phrase = input("Enter the phrase you would like to type. Add \'+\' between keys for a function \n"
                           "Use '\\+' if you want to input a plus")
        self.series = []
        plus_exists = False
        if phrase.count("+") != phrase.count("\\"):
            plus_exists = True

        phrase = re.sub(r'\\\+', '+', phrase)

        if plus_exists:
            self.setup_series(phrase)
            self.clean_input()

        else:
            self.series = list(phrase)

    def run(self):
        self.multi_input(0)

    def __str__(self):
        if self.series:
            return "Typing: " + ", ".join(map(str, self.series))
        return ""

    def multi_input(self, i):
        if i < len(self.series) - 1:
            with keyboard.pressed(self.series[i]):
                i += 1
                self.multi_input(i)
        else:
            keyboard.press(self.series[i])
            keyboard.release(self.series[i])

    def setup_series(self, phrase):
        while len(phrase) != 0:
            if '+' in phrase:
                self.series.append(phrase[:phrase.find('+')])
                phrase = phrase[phrase.find('+') + 1:]
            else:
                self.series.append(phrase)
                phrase = ''

    def clean_input(self):
        temp_series = [] + self.series
        self.series.clear()

        for i in range(len(temp_series)):
            if len(temp_series[i]) > 1:
                try:  # Crashes if you try to do a getattr with something like altt so need a try except
                    self.series.insert(0, getattr(Key, (temp_series[i])))  # More efficient than checking if
                except AttributeError:                                            # the command they input is ok
                    self.series += list(temp_series[i])
            else:
                self.series.append(temp_series[i])


class TypeTextUI(QtWidgets.QWidget):
    def __init__(self, main_app, parent=None):
        super(TypeTextUI, self).__init__(parent)
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)  # Main layout for the configuration view

        self.label = QLabel("Create a phrase to type")
        self.layout.addWidget(self.label)

        # Instructions label
        self.instruction_label = QLabel("Input the phrase below. Use + to indicate a command "
                                        "(e.g. ctrl+v or tab+)<br><br>"
                            "Use \\+ if you want to input +<br><br>"
                            "You can see all valid commands "
                            "<a href='https://pynput.readthedocs.io/en/latest/_modules/pynput"  # The docs are ugly but
                                        "/keyboard/_base.html#Key'>here</a>")  # there are way many commands to explain
        self.instruction_label.setOpenExternalLinks(True)
        self.layout.addWidget(self.instruction_label)

        self.layout.addWidget(self.instruction_label)

        # QLineEdit for text input
        self.text_input = QLineEdit()
        self.layout.addWidget(self.text_input)

        # Save button + logic
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(lambda: self.save_action())
        self.layout.addWidget(self.save_button)

        # Back button + logic
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(lambda: self.main_app.switch_to_main_view())
        self.layout.addWidget(self.back_button)

        self.wait_time = None

    def save_action(self):
        # Capture the text from the QLineEdit
        phrase = self.text_input.text()
        action = TypeText(phrase)
        self.main_app.add_action(action)
        self.main_app.switch_to_main_view()  # Switch back to the main view

    # def save_action(self):  # Currently the class handles errors, but this is here if I decide to revert that
    #     # Capture the text from the QLineEdit       # - would make it easier to give an error popup
    #     phrase = self.text_input.text()
    #     try:
    #         action = TypeText(phrase)
    #         self.main_app.add_action(action)
    #         self.main_app.switch_to_main_view()  # Switch back to the main view
    #     except AttributeError:
    #         QtWidgets.QMessageBox.warning(self, "Invalid Input",
    #                                       "You need to input valid commands.\nEither single letters,"
    #                                       "like v, c and x and / or a valid command like ctrl, alt or left.\n\n"
    #                                       "You can see all commands here: https://pynput.readthedocs.io/en/latest/keyboard.html")
