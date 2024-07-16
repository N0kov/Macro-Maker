from pynput.mouse import Button, Controller
from time import sleep

mouse = Controller()


# Clicks at the specified position. pos is the [x, y] coordinates and click_type is the type of click. Must be in the
# form Button.click
def click_pos(pos, click_type):
    mouse.position = (pos[0], pos[1])
    mouse.click(click_type, 1)


# Moves the mouse to a specified position. pos is the [x, y] coordinates
def mouse_to(pos):
    mouse.position = (pos[0], pos[1])


# Gets and returns the position of the mouse
def get_mouse_position():
    return mouse.position


# Drags the mouse between pos1 and pos2. These are coordinates in [x, y] form. Left click is held for the duration
def move_between(pos1, pos2):
    mouse_to(pos1)
    mouse.press(Button.left)
    sleep(.03)
    mouse_to(pos2)
    mouse.release(Button.left)


# Checks that a [x, y] coordinate set (input) is valid. If both x and y are floats or ints, they get returned in
# the form [x, y]. Floats are converted to ints. If one or both of them are not valid (ValueError if only
# there are not two values, TypeError if a bad type gets passed in), [0, 0] is returned instead.
def check_valid_input(input):
    try:  # Checking that both x and y are floats
        x = int(input[0])  # (10000, 10000) would just send to the bottom right, it wouldn't crash
        y = int(input[1])
        return [x, y]  # Forcing the correct format
    except (ValueError, TypeError):
        return [0, 0]  # In case bad data gets passed in
