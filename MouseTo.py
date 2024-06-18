from pyinput import mouse_to


class MouseTo:

    def __init__(self, x, y):
        self.coordinates = (x, y)

    def run(self):
        mouse_to(self.coordinates)

    def __str__(self):
        return "Mouse to (" + str(self.coordinates[0]) + ", " + str(self.coordinates[1]) + ")"

# Example usage:

# test = MouseTo(30, 50)
# test.run()
# print(test)