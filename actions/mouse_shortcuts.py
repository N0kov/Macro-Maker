from pynput.mouse import Button, Controller
from time import sleep
from PyQt6.QtWidgets import QComboBox

mouse = Controller()

# Windows has DPI scaling issues, so if on Windows these global flags need to be set. if os.name == 'nt'
# should check for Windows and only be True there, but as windll doesn't exist anywhere else, the
# except AttributeError is there for safety. See https://pypi.org/project/pynput/
import os
try:
    if os.name == 'nt':
        import ctypes
        PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
except AttributeError:
    pass


def move_between(pos1, pos2):
    """
    Drags the mouse between pos1 and pos2. These are coordinates in [x, y] form. Left click is held for the duration
    :param pos1: The initial x, y position for the mouse
    :param pos2: The final x, y position for the mouse
    """
    mouse.position = (pos1[0], pos1[1])
    mouse.press(Button.left)
    sleep(.03)
    mouse.position = (pos2[0], pos2[1])
    mouse.release(Button.left)


def check_valid_input(coordinates):
    """
    Checks that a [x, y] coordinate set (input) is valid. If both x and y are floats or ints, they get returned in
    the form [x, y]. Floats are converted to ints. If one or both of them are not valid (ValueError if only
    there are not two values, TypeError if a bad type gets passed in), [0, 0] is returned instead.
    :param coordinates: The x, y coordinates for a prospective mouse position. However, it is not restricted to this
    :return: A list that has x, y coordinates as [x, y]. If there was an error, [0, 0] is returned
    """
    try:  # Checking that both x and y are floats
        x = int(coordinates[0])  # (10000, 10000) would just send to the bottom right, it wouldn't crash
        y = int(coordinates[1])
        return [x, y]  # Forcing the correct format
    except (ValueError, TypeError):
        return [0, 0]  # In case bad data gets passed in


def create_macro_list(macro_list):
    i = 0
    macro_to_remove_box = QComboBox()
    while macro_list.itemText(i) != "Create a macro":
        macro_to_remove_box.addItem(macro_list.itemText(i))
        i += 1
    return macro_to_remove_box
