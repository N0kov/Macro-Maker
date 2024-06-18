from pyinput import clickPos
from pynput.mouse import Button
import time


class ClickX:

    def __init__(self, x, y, click_type):
        self.coordinates = (x, y)
        self.click = "Left"
        self.click_type = getattr(Button, "left")
        if click_type == "r":
            self.click_type = getattr(Button, "right")
            self.click = "Right"
        elif click_type == "m":
            self.click_type = getattr(Button, "middle")
            self.click = "Middle"

    def run(self):
        clickPos(self.coordinates, self.click_type)

    def __str__(self):
        return self.click + " click at (" + str(self.coordinates[0]) + ", " + str(self.coordinates[1]) + ")"


# Example usage:
# click1 = ClickX(330, 500, "right")
# click1.run()
# print(click1)