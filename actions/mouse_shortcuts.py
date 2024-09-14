from pynput.mouse import Button, Controller
from time import sleep

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


def set_click_type(click_type_string):
    """
    Takes a string in, processes if it is for a left, right or middle click and returns a string of that type,
    alongside the pynput form (Key.something). If the input isn't valid, None is returned for both
    :param click_type_string: A String, should be left, right or middle / l, r, m to get something other than None
    :return: A String representation of the click, then the click in pynput form
    """
    print(click_type_string)
    if click_type_string:
        click_type_string = click_type_string.lower()
        if click_type_string in ("l", "left"):
            click = "Left"
            click_type = Button.left
        elif click_type_string in ("r", "right"):
            click_type = Button.right
            click = "Right"
        else:
            click_type = Button.middle
            click = "Middle"
    else:
        click_type = None
        click = None

    return click, click_type
