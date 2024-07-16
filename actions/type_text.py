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
            print(self.series)

    def run(self):
        def multi_input(i):
            if i < len(self.series) - 1:
                with keyboard.pressed(self.series[i]):
                    i += 1
                    multi_input(i)
            else:
                keyboard.press(self.series[i])
                keyboard.release(self.series[i])

        multi_input(0)

        for key in self.series:  # for redundancy to guarantee that everything is released
            keyboard.release(key)

    def __str__(self):
        if self.series:
            return "Typing: " + ", ".join(map(str, self.series))
        return ""

    def setup_series(self, phrase):
        while len(phrase) != 0:
            if '+' in phrase:
                self.series.append(phrase[:phrase.find('+')])
                phrase = phrase[phrase.find('+') + 1:]
            else:
                self.series.append(phrase)
                phrase = ''

    def clean_input(self):
        directions = [Key.up, Key.right, Key.down, Key.left]
        temp_series = [] + self.series
        self.series.clear()

        for i in range(len(temp_series)):
            if len(temp_series[i]) > 1:
                try:  # Crashes if you try to do a getattr with something like altt so need a try except
                    temp_key = getattr(Key, (temp_series[i]))
                    if temp_key not in directions:  # The commands are inserted as if you were to type v+ctrl, nothing
                        self.series.insert(0, getattr(Key, (temp_series[i])))  # happens. They have to be first
                    else:  # for them to work
                        self.series.append(temp_key)
                except AttributeError:
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

        self.instruction_label = QLabel("Input the phrase below. Use + to indicate a command "
                                        "(e.g. ctrl+v or tab+)<br><br>"
                                        "Use \\+ if you want to input +<br><br>"
                                        "You can see all valid commands "
                                        "<a href='https://pynput.readthedocs.io/en/latest/_modules/pynput"
                                        "/keyboard/_base.html#Key'>here</a>")

        self.instruction_label.setOpenExternalLinks(True)
        self.layout.addWidget(self.instruction_label)

        self.layout.addWidget(self.instruction_label)

        self.text_input = QLineEdit()
        self.layout.addWidget(self.text_input)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(lambda: self.save_action())
        self.layout.addWidget(self.save_button)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(lambda: self.main_app.switch_to_main_view())
        self.layout.addWidget(self.back_button)

        self.wait_time = None

    def save_action(self):
        phrase = self.text_input.text()
        action = TypeText(phrase)
        self.main_app.add_action(action)
        self.main_app.switch_to_main_view()
