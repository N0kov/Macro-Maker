from pynput.keyboard import Key, Controller
from actions.action import Action
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QLineEdit
import re

keyboard = Controller()


class TypeText(Action):
    """
    An object that can take a phrase, interpret it to be individual keys or special keys (e.g. ctrl)
    and then type it back
    """

    def __init__(self, phrase):
        """
        Takes a String and converts it to a list that can be read by pynput. + denotes that it's a special key.
        Special keys are moved to the front, before alphanumeric ones
        :param phrase: A string. + denotes a special key
        """
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
        """
        Types self.series. All keys are pressed simultaneously
        """
        def multi_input(i):
            """
            Presses the current key (index i), then calls itself to press the next key in the series, etc.
            Akin to a for loop
            :param i: The current index for series
            """
            if i < len(self.series):
                with keyboard.pressed(self.series[i]):
                    i += 1
                    multi_input(i)

        multi_input(0)

        # for redundancy to guarantee that everything is released
        for key in self.series:
            keyboard.release(key)

    def __str__(self):
        """
        Returns a string representation of the TypeText object in the form "Typing [text here]". Text for example will
        look like: h, e, l, l, o,  , Key.something
        """
        if self.series:
            return "Typing: " + ", ".join(map(str, self.series))
        return ""

    def setup_series(self, phrase):
        """
        Separates the passed in string to a series of items in a list. + indicates that a new string should be made.
        The + is not included
        :param phrase: String, to be processed into substrings
        """
        while len(phrase) != 0:
            if '+' in phrase:
                self.series.append(phrase[:phrase.find('+')])
                phrase = phrase[phrase.find('+') + 1:]
            else:
                self.series.append(phrase)
                phrase = ''

    def clean_input(self):
        """
        Enumerates all strings in self.series that are longer than one character with Key. If an AttributeError
        is thrown due to an invalid string being passed in, it instead individually adds each character to self.series
        Enumerated keys, other than those in no_move (directly below this docstring) are placed at the front
        of self.series. The enum keys are moved because modifier keys must be hit first (e.g. v then control would
        not paste anything)
        """
        no_move = [Key.up, Key.right, Key.down, Key.left, Key.tab, Key.delete, Key.backspace]
        temp_series = [] + self.series
        self.series.clear()

        for i in range(len(temp_series)):
            if len(temp_series[i]) > 1:
                try:
                    temp_key = getattr(Key, (temp_series[i]))
                    if temp_key not in no_move:
                        self.series.insert(0, getattr(Key, (temp_series[i])))
                    else:
                        self.series.append(temp_key)
                except AttributeError:
                    self.series += list(temp_series[i])
            else:
                self.series.append(temp_series[i])


class TypeTextUI(QtWidgets.QWidget):
    """
    TypeText's UI. This allows the user to type a phrase into a box and have that be converted
    into a TypeText object which can be run at later notice
    """

    def __init__(self, main_app, parent=None):
        """
        Establishes the main application frame, and calls init_ui to do the rest
        :param main_app: The application that this is being called from
        :param parent: The parent widget. Defaults to None
        """
        super(TypeTextUI, self).__init__(parent)
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        """
        Initializes the UI elements
        """
        self.layout = QVBoxLayout(self)

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
        """
        Creates a TypeText object when the user hits the save button. This is based on the user's text_input
        It's then returned to UI3 and added to its action list
        :return: A TypeText object using the user's input which is sent to UI3
        """
        phrase = self.text_input.text()
        action = TypeText(phrase)
        self.main_app.add_action(action)
        self.main_app.switch_to_main_view()
