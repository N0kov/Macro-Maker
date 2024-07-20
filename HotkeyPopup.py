from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt


class HotkeyPopup(QDialog):
    """
    The popup for changing the start / stop hotkey. Captures the user's input and displays it to them. Returns to UI3
    after
    """
    def __init__(self, hotkey, parent=None):
        """
        Initializes the popup, and creates the buttons and labels. Sets the initial hotkey to be the passed in hotkey
        :param hotkey: The current hotkey that's being used to be displayed in hotkey_display. Must be a list
        :param parent: The parent widget. Defaults to None
        """
        super().__init__(parent)

        self.setWindowTitle("Hotkey")
        self.setGeometry(550, 300, 280, 180)

        self.layout = QVBoxLayout()

        self.recording = False

        self.label = QLabel("Set start/ stop hotkey")
        self.layout.addWidget(self.label)

        self.horizontal_layout = QHBoxLayout()

        self.start_button = QPushButton("Start", self)
        self.start_button.setFixedHeight(50)
        self.start_button.clicked.connect(self.start_recording)
        self.horizontal_layout.addWidget(self.start_button)

        self.key_combination = hotkey

        self.hotkey_display = QLabel(str(self.key_combination[0]))
        self.hotkey_display.setFixedHeight(50)
        self.hotkey_display.setAlignment(Qt.AlignCenter)
        self.horizontal_layout.addWidget(self.hotkey_display)

        self.layout.addLayout(self.horizontal_layout)
        self.layout.addSpacing(20)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def start_recording(self):
        """
        Starts recording the user's keystrokes, notifies the user of this via changing the top label. This
        happens on the start button being pressed, and the keystrokes are added to key_combination.
        This is currently limited at a single key
        """
        self.recording = True
        self.key_combination = []
        self.label.setText("Recording started. Press keys...")
        self.start_button.setEnabled(False)
        self.grabKeyboard()

    def stop_recording(self):
        """
        Once the user stops pressing any keys what they pressed is displayed to the user. Reverts the label to tell the
        user to press to create a new hotkey. This will only return the last key inputted
        """
        self.recording = False
        self.start_button.setEnabled(True)
        self.label.setText("Press start to start recording the new hotkey")
        if self.key_combination:
            self.hotkey_display.setText(str(self.key_combination[-1]))
        else:
            self.hotkey_display.setText("No hotkey")
        self.releaseKeyboard()

    def keyPressEvent(self, event):
        """
        Processes the key the user hit. This live updates the box that shows the current hotkey. If the user presses
        a key the recording will be stopped, and stop_recording() called. This only accepts unique keys, and the keys
        are stored in a pynput readable form
        :param event: A keystroke from the user
        """
        if self.recording:
            key = event.key()

            special_keys = {  # This is awful but event.key() doesn't seem to natively process to strings nicely so
                Qt.Key_Shift: 'shift',  # this is used
                Qt.Key_Control: 'ctrl',
                Qt.Key_Alt: 'alt',
                Qt.Key_Left: 'left',
                Qt.Key_Up: 'up',
                Qt.Key_Right: 'right',
                Qt.Key_Down: 'down',
                Qt.Key_Space: 'space',
                Qt.Key_Enter: 'enter',
                Qt.Key_Return: 'return',
                Qt.Key_Backspace: 'backspace',
                Qt.Key_Tab: 'tab',
                Qt.Key_Escape: 'escape',
                Qt.Key_F1: 'f1',
                Qt.Key_F2: 'f2',
                Qt.Key_F3: 'f3',
                Qt.Key_F4: 'f4',
                Qt.Key_F5: 'f5',
                Qt.Key_F6: 'f6',
                Qt.Key_F7: 'f7',
                Qt.Key_F8: 'f8',
                Qt.Key_F9: 'f9',
                Qt.Key_F10: 'f10',
                Qt.Key_F11: 'f11',
                Qt.Key_F12: 'f2',
                Qt.Key_Insert: 'insert',
                Qt.Key_Delete: 'delete',
                Qt.Key_Home: 'home',
                Qt.Key_End: 'end',
                Qt.Key_PageUp: 'page_up',
                Qt.Key_PageDown: 'page_down',
                Qt.Key_CapsLock: 'caps_lock',
                Qt.Key_NumLock: 'num_lock',
                Qt.Key_ScrollLock: 'scroll_lock',
                Qt.Key_Pause: 'pause',
                Qt.Key_Print: 'print_screen',
                Qt.Key_Menu: 'menu',
                Qt.Key_Super_L: 'cmd_l',
                Qt.Key_Super_R: 'cmd_r',
                Qt.Key_Clear: 'clear'
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
