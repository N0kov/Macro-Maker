from ImageDetect import compare_main, get_image
from MouseShortcuts import get_mouse_position
from Listener import start_listener, continue_script


class Image:

    def __init__(self):
        print("Setting the coordinates for the image.")
        print("Move your mouse to the top left of the image. Press shift when ready. ", end="")
        start_listener()
        while continue_script():
            pass
        top_left = [get_mouse_position()[0], get_mouse_position()[1]]
        print("\nMove your mouse to the bottom right of the image. Press shift when ready. ", end="")
        start_listener()
        while continue_script():
            pass
        bottom_right = [get_mouse_position()[0], get_mouse_position()[1]]
        self.check_sizes(top_left, bottom_right)
        self.coordinates = [[top_left[0], top_left[1]], [bottom_right[0], bottom_right[1]]]
        print("\nPress shift when you are ready to capture image. ", end="")
        start_listener()
        while continue_script():
            pass
        print()
        self.image = get_image(self.coordinates)

    def run(self):
        return compare_main(self.image, self.coordinates)

    @staticmethod
    def check_sizes(top_left, bottom_right):
        for index in range(len(top_left)):
            if top_left[index] > bottom_right[index]:
                temp = top_left[index]
                top_left[index] = bottom_right[index]
                bottom_right[index] = temp
