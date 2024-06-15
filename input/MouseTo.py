from pyinput import mouse_to

class MouseTo:

    def __init__(self, x, y):
        self.coordinates = (x, y)

    def run(self):
        mouse_to(self.coordinates)

# Example usage:

# Mo = MouseTo((30, 50))
# Mo.run()