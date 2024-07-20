from unittest import TestCase
from actions import MouseTo


class TestMouseTo(TestCase):
    pass

    def test_coordinate_passing_valid_data(self):
        coordinates = [30, 50]
        self.assertEqual(coordinates, MouseTo(coordinates).coordinates)
        self.assertEqual(coordinates, MouseTo(("30", "50")).coordinates)  # Passing a string is fine
        self.assertEqual(coordinates, MouseTo((30.2, 50.8)).coordinates)  # Decimals are floored


    def test_coordinates_passing_too_much_data(self):
        coordinates = [80, 70]
        self.assertEqual(coordinates, MouseTo((80, 70, 3)).coordinates)
        self.assertEqual(coordinates, MouseTo((80, 70, "9000")).coordinates)

    def test_coordinate_passing_too_little(self):
        top_left = [0, 0]

        self.assertEqual(top_left, MouseTo(50).coordinates)

    def test_str_method(self):
        self.assertEqual("Mouse to (1390, 123)", MouseTo((1390, 123)).__str__())

        self.assertEqual("Mouse to (0, 0)", MouseTo("should end up at (0, 0)").__str__())
