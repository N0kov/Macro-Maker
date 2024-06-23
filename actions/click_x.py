from actions.action import Action
from MouseShortcuts import click_pos, get_mouse_position
from pynput.mouse import Button
from Listener import start_listener, continue_script


class ClickX(Action):
    def __init__(self, coordinates=None, click_type=None):
        if coordinates == None:
            print("Move your mouse to the desired position. Press shift when ready. ", end="")
            start_listener()
            while continue_script():
                pass
            self.coordinates = (get_mouse_position()[0], get_mouse_position()[1])
            print()
        else:
            self.coordinates = coordinates
        if click_type == None:
            click_type = ""
            while click_type != "l" and click_type != "r" and click_type != "m":
                click_type = input("(L)eft, (R)ight or (M)iddle click? ").lower()

        self.click = "Left"
        self.click_type = getattr(Button, "left")
        if click_type == "r":
            self.click_type = getattr(Button, "right")
            self.click = "Right"
        elif click_type == "m":
            self.click_type = getattr(Button, "middle")
            self.click = "Middle"

    def run(self):
        click_pos(self.coordinates, self.click_type)

    def __str__(self):
        return self.click + " click at (" + str(self.coordinates[0]) + ", " + str(self.coordinates[1]) + ")"
