from actions.action import Action
from MouseShortcuts import move_between, get_mouse_position
from Listener import start_listener, continue_script


class SwipeXY(Action):
    def __init__(self):
        print("Move your mouse to the desired start position. Press shift when ready.", end="")
        start_listener()
        while continue_script():
            pass
        self.start = (get_mouse_position()[0], get_mouse_position()[1])
        print("\nMove your mouse to the desired end position. Press shift when ready.", end="")
        start_listener()
        while continue_script():
            pass
        self.end = (get_mouse_position()[0], get_mouse_position()[1])
        print()  # Clearing the end="" from above

    def run(self):
        move_between(self.start, self.end)

    def __str__(self):
        return "Swipe between ({0}, {1}) and ({2}, {3})".format(str(self.start[0]), str(self.start[1]),
                                                                str(self.end[0]), str(self.end[1]))
