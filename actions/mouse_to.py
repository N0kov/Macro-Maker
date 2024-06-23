from actions.action import Action
from MouseShortcuts import mouse_to, get_mouse_position
from Listener import start_listener, continue_script


class MouseTo(Action):
    def __init__(self, coordinates=None):
        if coordinates == None:
            print("Move your mouse to the desired position. Press shift when ready. ", end="")
            start_listener()
            while continue_script():
                pass
            self.coordinates = (get_mouse_position()[0], get_mouse_position()[1])
        else:
            self.coordinates = coordinates

    def run(self):
        mouse_to(self.coordinates)

    def __str__(self):
        return "Mouse to (" + str(self.coordinates[0]) + ", " + str(self.coordinates[1]) + ")"
