from PyQt5.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt


class HotkeyPopup(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Hotkey")
        self.setGeometry(550, 300, 270, 180)

        self.layout = QVBoxLayout()

        self.recording = False
        self.combination = []

        self.label = QLabel("Press start to start recording the hotkey")
        self.layout.addWidget(self.label)

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_recording)
        self.layout.addWidget(self.start_button)

        self.run_input = QLineEdit()
        self.layout.addWidget(self.run_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def start_recording(self):
        self.recording = True
        self.key_combination = []
        self.label.setText("Recording started. Press keys...")
        self.start_button.setEnabled(False)
        self.grabKeyboard()

    def stop_recording(self):
        self.recording = False
        if self.key_combination:
            captured_keys = ", ".join(self.key_combination)
        else:
            captured_keys = "No keys captured"
        self.label.setText("Recording stopped. The hotkey is " + str(captured_keys))
        self.start_button.setEnabled(True)
        self.releaseKeyboard()

    def keyPressEvent(self, event):
        if self.recording:
            key = event.key()

            special_keys = {  # This is awful but event.key() with special characters is weird, so I'm doing this
                Qt.Key_Shift: 'shift',
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

            if key in special_keys:
                key_name = special_keys[key]
            else:
                try:
                    key_name = chr(key)
                except ValueError:  # If you hit a modifier key that isn't defined above
                    key_name = f'Key_{key}'

            if key_name not in self.key_combination:
                self.key_combination.append(key_name)
                self.label.setText(f"Capturing: {', '.join(self.key_combination)}")  # Don't like printf but not sure
                                                                                     # how to represent this otherwise

    def keyReleaseEvent(self, event):
        if self.recording:
            self.recording = False
            self.stop_recording()
