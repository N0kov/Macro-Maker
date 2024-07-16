from pynput.mouse import Button, Controller
from time import sleep

mouse = Controller()


# Drags the mouse between pos1 and pos2. These are coordinates in [x, y] form. Left click is held for the duration
def move_between(pos1, pos2):
    mouse.position = (pos1[0], pos1[1])
    mouse.press(Button.left)
    sleep(.03)
    mouse.position = (pos2[0], pos2[1])
    mouse.release(Button.left)


# Checks that a [x, y] coordinate set (input) is valid. If both x and y are floats or ints, they get returned in
# the form [x, y]. Floats are converted to ints. If one or both of them are not valid (ValueError if only
# there are not two values, TypeError if a bad type gets passed in), [0, 0] is returned instead.
def check_valid_input(coordinates):
    try:  # Checking that both x and y are floats
        x = int(coordinates[0])  # (10000, 10000) would just send to the bottom right, it wouldn't crash
        y = int(coordinates[1])
        return [x, y]  # Forcing the correct format
    except (ValueError, TypeError):
        return [0, 0]  # In case bad data gets passed in
