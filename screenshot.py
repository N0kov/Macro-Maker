#!/usr/bin/env python3

from pynput.keyboard import Key, Controller, Listener
from pynput.mouse import Button, Controller as MouseController
import time
import pyinput

keyboard = Controller()
mouse = MouseController()

# top_left = [240, 112]
# bottom_right = [640, 194]
top_left = [93, 116]
bottom_right = [483, 210]
screenshot_pos = [70, 233]

# time.sleep(2)
# pyinput.mousePos()



def take_section():
    with keyboard.pressed(Key.cmd_l):
        with keyboard.pressed(Key.shift):
            keyboard.press(Key.print_screen)
            time.sleep(.1)
            keyboard.release(Key.print_screen)
    time.sleep(1.3)
    pyinput.move_between(top_left, bottom_right)


def take_specific_section(left_top, right_bottom):
    time.sleep(.05)
    with keyboard.pressed(Key.cmd_l):
        with keyboard.pressed(Key.shift):
            keyboard.press(Key.print_screen)
            time.sleep(.1)
            keyboard.release(Key.print_screen)
    time.sleep(1.5)
    pyinput.move_between(left_top, right_bottom)

# time.sleep(.3)
# take_section()
# time.sleep(1)
# pyinput.move_between(top_left, bottom_right)

# pyinput.mouse_to(top_left)
# time.sleep(2)
# pyinput.mousePos()
# pyinput.mouse_to(bottom_right)