from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
import inflect


class HotkeyPopup(QDialog):
    """
    The popup for changing the start / stop hotkey. Captures the user's input and displays it to them. Returns to UI3
    after
    """
    def __init__(self, hotkey, all_hotkeys, parent=None):
        """
        Initializes the popup, and creates the buttons and labels. Sets the initial hotkey to be the passed in hotkey
        :param hotkey: The hotkey in the given list that is in use
        :param all_hotkeys: All hotkeys currently in use. Must be a list
        :param parent: The parent widget. Defaults to None
        """
        super().__init__(parent)

        self.setWindowTitle("Set a Hotkey")
        self.setGeometry(550, 300, 280, 180)

        layout = QVBoxLayout()

        self.recording = False

        self.label = QLabel("Press start to record a hotkey")
        layout.addWidget(self.label)

        horizontal_layout = QHBoxLayout()

        self.start_button = QPushButton("Start", self)
        self.start_button.setFixedHeight(50)
        self.start_button.clicked.connect(self.start_recording)
        horizontal_layout.addWidget(self.start_button)

        self.key_combination = all_hotkeys[hotkey]
        self.old_hotkey = all_hotkeys[hotkey]
        self.bad_hotkeys = all_hotkeys[:hotkey] + [""] + all_hotkeys[hotkey+1:]

        self.hotkey_display = QLabel(str(self.key_combination))
        self.hotkey_display.setFixedHeight(50)
        self.hotkey_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        horizontal_layout.addWidget(self.hotkey_display)

        layout.addLayout(horizontal_layout)
        layout.addSpacing(20)

        remove_hotkey = QPushButton("Remove Hotkey")

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        button_box.addButton(remove_hotkey, QDialogButtonBox.ButtonRole.ActionRole)

        button_box.accepted.connect(self.accept)
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
        self.label.setText("Press start to record a new hotkey")
        self.start_button.setText("Start")
        if self.key_combination:
            if self.key_combination[-1] not in self.bad_hotkeys:
                self.hotkey_display.setText(str(self.key_combination[-1]))
            else:
                self.label.setText("Macro " + inflect.engine().number_to_words(self.bad_hotkeys.index(
                                                                               self.key_combination[0]) + 1) +
                                   " is already using " + str(self.key_combination[0]) +
                                   "\n\n" + self.label.text() + "\n")

                self.key_combination = ""
                self.hotkey_display.setText("No hotkey")

        else:
            self.hotkey_display.setText("No hotkey")
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

            special_keys = {  # This is awful but event.key() doesn't seem to natively process to strings nicely so
                Qt.Key.Key_Shift: 'shift',  # this is used
                Qt.Key.Key_Control: 'ctrl',
                Qt.Key.Key_Alt: 'alt',
                Qt.Key.Key_Left: 'left',
                Qt.Key.Key_Up: 'up',
                Qt.Key.Key_Right: 'right',
                Qt.Key.Key_Down: 'down',
                Qt.Key.Key_Space: 'space',
                Qt.Key.Key_Enter: 'enter',
                Qt.Key.Key_Return: 'return',
                Qt.Key.Key_Backspace: 'backspace',
                Qt.Key.Key_Tab: 'tab',
                Qt.Key.Key_Escape: 'escape',
                Qt.Key.Key_F1: 'f1',
                Qt.Key.Key_F2: 'f2',
                Qt.Key.Key_F3: 'f3',
                Qt.Key.Key_F4: 'f4',
                Qt.Key.Key_F5: 'f5',
                Qt.Key.Key_F6: 'f6',
                Qt.Key.Key_F7: 'f7',
                Qt.Key.Key_F8: 'f8',
                Qt.Key.Key_F9: 'f9',
                Qt.Key.Key_F10: 'f10',
                Qt.Key.Key_F11: 'f11',
                Qt.Key.Key_F12: 'f2',
                Qt.Key.Key_Insert: 'insert',
                Qt.Key.Key_Delete: 'delete',
                Qt.Key.Key_Home: 'home',
                Qt.Key.Key_End: 'end',
                Qt.Key.Key_PageUp: 'page_up',
                Qt.Key.Key_PageDown: 'page_down',
                Qt.Key.Key_CapsLock: 'caps_lock',
                Qt.Key.Key_NumLock: 'num_lock',
                Qt.Key.Key_ScrollLock: 'scroll_lock',
                Qt.Key.Key_Pause: 'pause',
                Qt.Key.Key_Print: 'print_screen',
                Qt.Key.Key_Menu: 'menu',
                Qt.Key.Key_Super_L: 'cmd_l',
                Qt.Key.Key_Super_R: 'cmd_r',
                Qt.Key.Key_Clear: 'clear'
            }

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

    def reject_with_old_hotkey(self):
        self.key_combination = self.old_hotkey
        self.reject()

    def close_without_hotkey(self):
        self.key_combination = []
        self.accept()
