from actions.action import Action
from actions.mouse_shortcuts import set_click_type

from pynput.mouse import Controller, Button
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QWidget


class NudgeMouse(Action):
    def __init__(self, increment, click_type):
        self.increment = increment
        self.click, self.click_type = set_click_type(click_type)

    def __str__(self):
        return_string = "Moving the mouse "

        if self.increment[1] != 0:
            if self.increment[0] > 0:
                return_string = return_string + str(self.increment[0]) + " pixels right and "
            elif self.increment[0] < 0:
                return_string = return_string + str(-self.increment[0]) + " pixels left and "
            if self.increment[1] < 0:  # Pynput considers 0 to be the top of the screen, so increment must be negative
                return_string = return_string + str(-self.increment[1]) + " pixels up"  # to move up
            else:
                return_string = return_string + str(self.increment[1]) + " pixels down"

        else:
            if self.increment[0] > 0:
                return_string = return_string + str(self.increment[0]) + " pixels right"
            else:
                return_string = return_string + str(-self.increment[0]) + " pixels left"

        if self.click:
            return_string = return_string + " while " + self.click.lower() + " clicking"

        return return_string

    def run(self):
        if self.click_type:
            Controller().press(self.click_type)
            Controller().position = (self.increment[0] + Controller().position[0],
                                     self.increment[1] + Controller().position[1])
            Controller().release(self.click_type)
        else:
            Controller().position = (self.increment[0] + Controller().position[0],
                                     self.increment[1] + Controller().position[1])

    def update_fields(self, increment, click_held):
        self.__init__(increment, click_held)


class NudgeMouseUI(QWidget):
    def __init__(self, main_app, nudge_mouse_to_edit=None):
        """
        Establishes the main application frame, and calls init_ui to do the rest
        :param main_app: The application that this is being called from
        :param nudge_mouse_to_edit: The passed in NudgeMouse action to be edited. Defaults to None
        """
        super(NudgeMouseUI, self).__init__()
        self.main_app = main_app
        self.init_ui(nudge_mouse_to_edit)

    def init_ui(self, nudge_mouse_to_edit=None):
        """
        Initializes the UI elements
        """
        self.layout = QVBoxLayout(self)

        self.title = QLabel("Create a new nudge mouse action")
        self.layout.addWidget(self.title)

        self.x_axis_prompt = QLabel("Input the number of pixels in the x axis the mouse should move:")
        self.layout.addWidget(self.x_axis_prompt)

        self.x_axis_text_input = QLineEdit()
        self.layout.addWidget(self.x_axis_text_input)

        self.y_axis_prompt = QLabel("y axis:")
        self.layout.addWidget(self.y_axis_prompt)

        self.y_axis_text_input = QLineEdit()
        self.layout.addWidget(self.y_axis_text_input)

        hold_mouse_prompt = QLabel("Should the mouse be held down?")
        self.layout.addWidget(hold_mouse_prompt)

        self.hold_mouse_box = QComboBox()
        self.hold_mouse_box.addItems(["No", "Yes"])
        self.hold_mouse_box.currentIndexChanged.connect(self.switch_held_choice)
        self.layout.addWidget(self.hold_mouse_box)

        self.click_type_label = QLabel("Select Click Type:")
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(["Left", "Right", "Middle"])
        self.layout.addWidget(self.click_type_label)
        self.layout.addWidget(self.click_type_combo)

        if nudge_mouse_to_edit:
            self.x_axis_text_input.setText(str(nudge_mouse_to_edit.increment[0]))
            self.y_axis_text_input.setText(str(-nudge_mouse_to_edit.increment[1]))
            if nudge_mouse_to_edit.click:
                self.hold_mouse_box.blockSignals(True)
                self.hold_mouse_box.setCurrentIndex(1)
                self.hold_mouse_box.blockSignals(False)

                if nudge_mouse_to_edit.click == "Right":
                    self.click_type_combo.setCurrentIndex(1)
                elif nudge_mouse_to_edit.click == "Middle":
                    self.click_type_combo.setCurrentIndex(2)
            else:
                self.click_type_label.hide()
                self.click_type_combo.hide()
        else:
            self.click_type_label.hide()
            self.click_type_combo.hide()

        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_action(nudge_mouse_to_edit))
        self.layout.addWidget(save_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.main_app.switch_to_main_view)
        self.layout.addWidget(back_button)

    def switch_held_choice(self):
        if self.hold_mouse_box.currentText() == "No":
            self.click_type_label.hide()
            self.click_type_combo.hide()
        else:
            self.click_type_label.show()
            self.click_type_combo.show()

    def save_action(self, nudge_mouse_to_edit):
        """
        If coordinates exist, this creates a NudgeMouse object using self.coordinates, and returns it
         to UI3's action list. If coordinates is None, nothing happens
        """
        x = self.x_axis_text_input.text()
        y = self.y_axis_text_input.text()
        try:
            x = int(x)
        except ValueError:
            x = 0
        try:
            y = -int(y)  # Pynput considers 0 as the top of the screen, which isn't intuitive, so flipping it here
        except ValueError:  # to make it more logical for the user
            y = 0

        if x != 0 or y != 0:
            if nudge_mouse_to_edit:
                if self.hold_mouse_box.currentText() == "Yes":
                    nudge_mouse_to_edit.update_fields([x, y], self.click_type_combo.currentText())
                else:
                    nudge_mouse_to_edit.update_fields([x, y], None)
                self.main_app.update_action_list()
            else:
                if self.hold_mouse_box.currentText() == "Yes":
                    action = NudgeMouse([x, y], self.click_type_combo.currentText())
                else:
                    action = NudgeMouse([x, y], None)
                self.main_app.add_action(action)
        self.main_app.switch_to_main_view()

