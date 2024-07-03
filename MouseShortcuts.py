from pynput.mouse import Button, Controller
from time import sleep

mouse = Controller()


def click_pos(pos, click_type):
    mouse.position = (pos[0], pos[1])
    mouse.click(click_type, 1)


def mouse_to(pos):
    mouse.position = (pos[0], pos[1])


def get_mouse_position():
    return mouse.position


def move_between(pos1, pos2):
    mouse_to(pos1)
    mouse.press(Button.left)
    sleep(.1)
    mouse_to(pos2)
    mouse.release(Button.left)
