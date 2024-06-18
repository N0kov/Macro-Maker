from pyinput import move_between

class SwipeXY:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def run(self):
        move_between(self.start, self.end)

    def __str__(self):
        return "Swipe between ({0}, {1}) and ({2}, {3})".format(str(self.start[0]), str(self.start[1]),
                                                                str(self.end[0]), str(self.end[1]))

# Example usage:
# test = SwipeXY((362, 192), (864, 537))
# test.run()
# print(test)