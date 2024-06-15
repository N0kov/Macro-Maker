from pyinput import move_between

class SwipeXY:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def run(self):
        move_between(self.start, self.end)

# Example usage:
# swipe1 = SwipeXY((362, 192), (864, 537))
# swipe1.swipe()