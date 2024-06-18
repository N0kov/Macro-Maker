from pynput.keyboard import Controller
from pynput.mouse import Button, Controller as MouseController
import time

keyboard = Controller()
mouse = MouseController()

def input_key(key):
    keyboard.press(key)
    keyboard.release(key)


def multi_input(keys, i):
    if i < len(keys) - 1:
        with keyboard.pressed(keys[i]):
            i += 1
            multi_input(keys, i)
    else:
        input_key(keys[i])

def clickPos(pos, click_type):
    mouse.position = (pos[0], pos[1])
    mouse.click(click_type, 1)

def mouse_to(pos):
    mouse.position = (pos[0], pos[1])

def mouse_postion():
    print(f"The current mouse position is {mouse.position}")

def get_mouse_positon():
    return mouse.position

def move_between(pos1, pos2):
    mouse_to(pos1)
    mouse.press(Button.left)
    time.sleep(.1)
    mouse_to(pos2)
    mouse.release(Button.left)