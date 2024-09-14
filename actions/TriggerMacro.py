from actions.action import Action
from misc_utilities.UI_helper import create_macro_list
from misc_utilities.listener import trigger_by_index

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton


class TriggerMacro(Action):
    def __init__(self, macro_index, macro_name):
        """
        Initializes TriggerMacro, sets the index macro that should be triggered,
        alongside the name of the macro
        :param macro_index: The index (int) of the macro to be triggered
        :param macro_name: The name (String) of the macro to be triggered
        """
        self.macro_index = macro_index
        self.macro_name = macro_name

    def __str__(self):
        """
        Returns "Triggering" followed by the name of the macro
        """
        return "Triggering " + str(self.macro_name)

    def run(self):
        """
        Triggers the macro that corresponds to the index in UI3's macro list
        """
        trigger_by_index(self.macro_index)

    def update_fields(self, alter_distance, new_macro_name):
        """
        Sets a new name, and adjusts macro_index by whatever the user passed in
        :param alter_distance: The amount that the macro index should be increased / decreased by (int)
        :param new_macro_name: The new name for the macro
        """
        self.macro_index = alter_distance + self.macro_index
        self.macro_name = new_macro_name

    def reset_fields(self, macro_index, macro_name):
        """
        Sets TriggerMacro to have a new name and index
        :param macro_index: The index (int) of the macro to be triggered
        :param macro_name: The name (String) of the macro to be triggered
        """
        self.macro_index = macro_index
        self.macro_name = macro_name

    @property
    def get_index(self):
        """
        Returns the index stored in macro_index
        :return: self.macro_index
        """
        return self.macro_index


class TriggerMacroUI(QtWidgets.QWidget):
    def __init__(self, main_app, macro_list, current_choice=None):
        """
        Establishes the main application frame, and calls init_ui to do the rest
        :param main_app: The application that this is being called from
        :param macro_list: A QComboBox containing all currently existing macros
        :param current_choice: The option the user selected previously, not required
        """
        super(TriggerMacroUI, self).__init__()
        self.main_app = main_app
        self.init_ui(macro_list, current_choice)

    def init_ui(self, macro_list, current_choice):
        """
        Initializes the UI elements
        """
        layout = QVBoxLayout(self)

        title = QLabel("Choose a macro to trigger")
        layout.addWidget(title)

        prompt = QLabel("Pick the macro:")
        layout.addWidget(prompt)

        self.macro_box = create_macro_list(macro_list)
        layout.addWidget(self.macro_box)
        if current_choice:
            self.macro_box.setCurrentIndex(current_choice.macro_index)

        # Allowing a macro to trigger itself causes problems, so it isn't allowed. Maybe allow this in the future?
        self.macro_box.removeItem(self.main_app.macro_list.currentIndex())

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(lambda: self.save_action(current_choice))
        layout.addWidget(self.save_button)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.main_app.switch_to_main_view)
        layout.addWidget(self.back_button)

    def save_action(self, current_choice):
        if self.macro_box.currentIndex() < self.main_app.macro_list.currentIndex():
            self.macro_index = self.macro_box.currentIndex()
        else:
            self.macro_index = self.macro_box.currentIndex() + 1

        if current_choice:
            current_choice.reset_fields(self.macro_index, self.macro_box.currentText())
            self.main_app.update_action_list()
        else:
            action = TriggerMacro(self.macro_index, self.macro_box.currentText())
            self.main_app.add_action(action)
        self.main_app.switch_to_main_view()
