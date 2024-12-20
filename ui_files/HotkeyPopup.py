from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from num2words import num2words
from misc_utilities.UI_helper import create_macro_list_names
from misc_utilities.special_keys import special_keys


class HotkeyPopup(QDialog):
    """
    The popup for changing the start / stop hotkey. Captures the user's input and displays it to them. Returns to UI3
    after
    """

    def __init__(self, hotkey, all_hotkeys, break_key, macro_list, current_macro, parent=None):
        """
        Initializes the popup, and creates the buttons and labels. Sets the initial hotkey to be the passed in hotkey
        :param hotkey: The hotkey in the given list that is in use
        :param all_hotkeys: All hotkeys currently in use. Must be a list
        :break_key: The current key to kill all macros. Must be a string
        :param parent: The parent widget. Defaults to None
        """
        super().__init__(parent)

        self.setWindowTitle("Set a Hotkey")
        self.setGeometry(550, 300, 280, 180)

        layout = QVBoxLayout()

        self.recording = False

        self.label = QLabel("Press start to record a hotkey")
        layout.addWidget(self.label)

        layout.addSpacing(5)

        horizontal_layout = QHBoxLayout()

        self.start_button = QPushButton("Start", self)
        self.start_button.setFixedHeight(50)
        self.start_button.clicked.connect(self.start_recording)
        horizontal_layout.addWidget(self.start_button)

        self.key_combination = all_hotkeys[hotkey]
        self.old_hotkey = all_hotkeys[hotkey]
        self.bad_hotkeys = all_hotkeys[:hotkey] + [""] + all_hotkeys[hotkey+1:]
        self.break_key = break_key
        self.macro_index = current_macro

        self.hotkey_display = QLabel(str(self.key_combination))
        self.hotkey_display.setFixedHeight(50)
        self.hotkey_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        horizontal_layout.addWidget(self.hotkey_display)

        layout.addLayout(horizontal_layout)
        layout.addSpacing(5)

        self.hotkey_location = QComboBox()
        self.hotkey_location.addItems(["Universal break key"] + create_macro_list_names(macro_list))
        self.hotkey_location.setCurrentIndex(current_macro + 1)
        self.hotkey_location.currentIndexChanged.connect(lambda: self.hotkey_location_changed(all_hotkeys))
        layout.addWidget(self.hotkey_location)

        layout.addSpacing(15)

        remove_hotkey = QPushButton("Remove Hotkey")

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        button_box.addButton(remove_hotkey, QDialogButtonBox.ButtonRole.ActionRole)

        button_box.accepted.connect(self.save_hotkey)
        button_box.rejected.connect(self.reject_with_old_hotkey)
        remove_hotkey.clicked.connect(self.close_without_hotkey)

        layout.addWidget(button_box)

        self.setLayout(layout)

        self.installEventFilter(self)

    def eventFilter(self, source, event):
        """
        Checks for if escape is pressed, and if so closes the popup
        :param source: The class that sent the message
        :param event: The key that was pressed in the form of a Qt KeyPress event
        :return: Standard eventFilter operations if the key is not escape
        """
        if event.type() == QtCore.QEvent.Type.KeyPress and event.key() == QtCore.Qt.Key.Key_Escape:
            self.reject()
        return super(HotkeyPopup, self).eventFilter(source, event)

    def start_recording(self):
        """
        Starts recording the user's keystrokes, notifies the user of this via changing the top label. This
        happens on the start button being pressed, and the keystrokes are added to key_combination.
        This is currently limited at a single key
        """
        self.recording = True
        self.key_combination = []
        self.label.setText("Recording started. Press keys...")
        self.start_button.setText("Recording")
        self.start_button.setEnabled(False)
        self.grabKeyboard()

    def stop_recording(self):
        """
        Once the user stops pressing any keys what they pressed is displayed to the user. Reverts the label to tell the
        user to press to create a new hotkey. This will only return the last key inputted
        """
        self.recording = False
        self.start_button.setEnabled(True)
        self.start_button.setText("Start")
        self.update_hotkey_display()
        self.releaseKeyboard()

    def keyPressEvent(self, event):
        """
        Processes the key the user hit. This live updates the box that shows the current hotkey. If the user presses
        a key the recording will be stopped, and stop_recording() called. This only accepts unique keys, and the keys
        are stored in a pynput readable form
        :param event: A keystroke from the user (Qt KeyPress)
        """
        if self.recording:
            key = event.key()
            key_name = None

            if key in special_keys:
                key_name = special_keys[key]
            else:
                try:
                    if "shift" in self.key_combination:
                        key_name = chr(key)  # Have to check for caps as it doesn't seem to differentiate
                        self.key_combination.remove("shift")
                    else:
                        key_name = chr(key).lower()  # It seems to default to caps so need lower()

                except ValueError:  # If you hit a modifier key that isn't defined above
                    self.hotkey_display.setText("Invalid key")

            if key_name:
                if key_name not in self.key_combination:  # Making sure that we only have unique keys
                    self.key_combination.append(key_name)
                    self.hotkey_display.setText("Capturing: " + str(self.key_combination[-1]))

            if len(self.key_combination) >= 1 and "shift" not in self.key_combination:
                self.recording = False
                self.stop_recording()

    def keyReleaseEvent(self, event):
        """
        Happens when the first key pressed is released. This the key recording, triggering stop_recording()
        :param event: A keystroke from the user
        """
        if self.recording:
            self.recording = False
            self.stop_recording()

    def update_hotkey_display(self):
        """
        Updates the hotkey display. If key combination is empty, it prompts the user to record a hotkey, and
        labels the hotkey display as "No hotkey". If it matches a prexesting hotkey it notifies the user, clears
        the hotkey and prompts the user for a new hotkey. Otherwise, it sets the hotkey display to be the current
        text
        """
        self.label.setText("Press start to record a hotkey")
        if type(self.key_combination) is list:
            text = self.key_combination[-1]
        else:
            text = self.key_combination
        if text != "":
            if text in self.bad_hotkeys and self.key_combination:
                self.label.setText("Macro " + num2words(self.bad_hotkeys.index(text) + 1) +
                                   " is already using " + text + "\n" + self.label.text())

                self.key_combination = ""
                self.hotkey_display.setText("No hotkey")

            elif text == self.break_key and self.hotkey_location.currentIndex() != 0:
                self.label.setText("The break key is already using " + self.break_key + "\n" + self.label.text())
                self.key_combination = ""
                self.hotkey_display.setText("No hotkey")

            else:
                self.hotkey_display.setText(text)

    def hotkey_location_changed(self, all_hotkeys):
        """
        Switches the UI to be based around the hotkey of the option that's currently selected, and updates
        it in case of any issues. Sets the key combination to that of the current macro if there currently isn't one
        """
        self.bad_hotkeys = all_hotkeys
        new_index = self.hotkey_location.currentIndex()
        if new_index == 0:
            self.old_hotkey = None
        else:
            self.old_hotkey = all_hotkeys[new_index - 1]
            self.bad_hotkeys = all_hotkeys[:new_index - 1] + [""] + all_hotkeys[new_index:]
        self.update_hotkey_display()
        if self.key_combination == "":
            if new_index == 0 and self.break_key != "":
                self.key_combination = self.break_key
            elif all_hotkeys[new_index - 1] != "":
                self.key_combination = all_hotkeys[new_index - 1]
            else:
                return
            self.update_hotkey_display()

    def reject_with_old_hotkey(self):
        """
        Sets the key combination to the old hotkey, then closes the window
        """
        self.key_combination = self.old_hotkey
        self.reject()

    def close_without_hotkey(self):
        """
        Sets the key combination to be nothing, then closes the window
        """
        self.key_combination = ""
        self.accept()

    def save_hotkey(self):
        """
        If the key combination is a list, turns it into a string. From there, it closes the window
        """
        try:
            if list is type(self.key_combination):
                self.key_combination = self.key_combination[0]
        except (AttributeError, IndexError):
            pass

        self.accept()
