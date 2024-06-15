from pyinput import clickPos

class ClickX:

    def __init__(self, x, y):
        self.coordinates = (x, y)

    def run(self):
        clickPos(self.coordinates)


# Example usage:
# click1 = ClickX(330, 500)
# click1.run()