from PyQt6.QtCore import Qt


# The list of unique keys that can be seen from Qt when a key is pressed
special_keys = {
                Qt.Key.Key_Shift: 'shift',
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