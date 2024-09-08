from actions.action import Action
from actions.mouse_shortcuts import set_click_type

from pynput.mouse import Controller
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QWidget


class NudgeMouse(Action):
    def __init__(self, increment, click_type):
        """
        Initializes NudgeMouse. Increment is how much the mouse should be moved by, click is a String representation
        of what click should be performed (if any), and click_type is the click in pynput form (if any)
        :param increment: An array, in the form [x, y] (must be ints)
        :param click_type: A string, to not return None, must be either "left", "right", or "middle" (or l / r / m)
        """
        self.increment = increment
        self.click, self.click_type = set_click_type(click_type)

    def __str__(self):
        """
        Returns a String saying how much the mouse should move, and if it is holding down click or not
        (and what type of click that is)
        """
        x_move = str(abs(self.increment[0]))
        y_move = str(abs(self.increment[1]))

        x_dir = "right" if self.increment[0] > 0 else "left"
        y_dir = "up" if self.increment[1] < 0 else "down"  # Have to reflip it here

        return_string = "Moving the mouse "

        if self.increment[1] != 0:
            if self.increment[0] != 0:
                return_string += x_move + " pixels " + x_dir + " and " + y_move + " pixels " + y_dir
            else:
                return_string += y_move + " pixels " + y_dir
        else:
            return_string += x_move + " pixels " + x_dir

        if self.click:
            return_string += " while " + self.click.lower() + " clicking"

        return return_string

    def run(self):
        """
        Moves the mouse a number of pixels in the x and y directions, as specified in self.increment.
        Can also hold down left, right or middle click during this time as specified by self.click_type
        """
        if self.click_type:
            Controller().press(self.click_type)
            Controller().position = (self.increment[0] + Controller().position[0],
                                     self.increment[1] + Controller().position[1])
            Controller().release(self.click_type)
        else:
            Controller().position = (self.increment[0] + Controller().position[0],
                                     self.increment[1] + Controller().position[1])

    def update_fields(self, increment, click_type):
        """
        Updates the increment and click_type instance variables as specified by the data passed in
        :param increment: An array, in the form [x, y] (must be ints)
        :param click_type: A string, to not return None, must be either "left", "right", or "middle" (or l / r / m)

        """
        self.__init__(increment, click_type)


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
        """
        If the user switches the hold_mouse_box to say that they want a click to be held, makes the option to set
        a click (and the prompt) appear. If they say they don't want a click, it instead hides the box and label
        """
        if self.hold_mouse_box.currentText() == "No":
            self.click_type_label.hide()
            self.click_type_combo.hide()
        else:
            self.click_type_label.show()
            self.click_type_combo.show()

    def save_action(self, nudge_mouse_to_edit):
        """
        If coordinates exist, this creates a NudgeMouse object using self.coordinates,
        and returns it to UI3's action list. If coordinates is None, nothing happens
        """
        x = self.x_axis_text_input.text()
        y = self.y_axis_text_input.text()
        try:
            x = int(x)
        except ValueError:
            x = 0
        try:
            y = -int(y)  # Pynput considers 0 as the top of the screen, which isn't intuitive, while a normal
        except ValueError:  # user would most likely consider positive to be up, so it has to be flipped here
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
