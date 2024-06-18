# from ImageDetect import get_image, compare_main
import ImageDetect


class Image:

    def __init__(self, top_left, bottom_right):
        self.check_sizes(top_left, bottom_right)
        self.coordinates = [[top_left[0], top_left[1]], [bottom_right[0], bottom_right[1]]]
        self.image = ImageDetect.get_image(self.coordinates)

    def run(self):
        return ImageDetect.compare_main(self.image, self.coordinates)

    @staticmethod
    def check_sizes(top_left, bottom_right):
        for index in range(len(top_left)):
            if top_left[index] > bottom_right[index]:
                temp = top_left[index]
                top_left[index] = bottom_right[index]
                bottom_right[index] = temp


# thing = Image([50, 80], [20, 500])
#
# print(thing.run())
