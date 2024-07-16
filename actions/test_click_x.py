from unittest import TestCase
from actions import click_x
from pynput.mouse import Button


class TestClickX(TestCase):
    def test_coordinate_passing_valid_data(self):
        coordinates = [30, 50]
        self.assertEqual(coordinates, click_x.ClickX(coordinates, "left").coordinates)

    def test_coordinates_passing_too_much_data(self):
        coordinates = [80, 70]
        self.assertEqual(coordinates, click_x.ClickX((80, 70, 3), "right").coordinates)
        self.assertEqual(coordinates, click_x.ClickX((80, 70, "3"), "middle").coordinates)

    def test_coordinate_passing_invalid_data(self):
        top_left = [0, 0]
        self.assertEqual(top_left, click_x.ClickX(50, "bad").coordinates)

        three_eight = [300, 8000]
        self.assertEqual(three_eight, click_x.ClickX(("300", "8000"), "a").coordinates)  # It takes strings fine

    def test_click_type_valid(self):
        default_click = click_x.ClickX((50, 30), "not a click")
        self.assertEqual(Button.left, default_click.click_type)

        left_test_l = click_x.ClickX((51, 31), "l")
        self.assertEqual(Button.left, left_test_l.click_type)

        left_test_left = click_x.ClickX((54, 14), "left")
        self.assertEqual(Button.left, left_test_left.click_type)

        right_test_r = click_x.ClickX((146, 642), "r")
        self.assertEqual(Button.right, right_test_r.click_type)

        right_test_right = click_x.ClickX((752, 457), "right")
        self.assertEqual(Button.right, right_test_right.click_type)

        middle_test_m = click_x.ClickX((30, 290), "m")
        self.assertEqual(Button.middle, middle_test_m.click_type)

        middle_test_middle = click_x.ClickX("the coordinates do not matter", "middle")
        self.assertEqual(Button.middle, middle_test_middle.click_type)

    def test_invalid_click_type(self):
        self.assertEqual(Button.left, click_x.ClickX((50, 30), "this is not a valid input").click_type)

        self.assertEqual(Button.left, click_x.ClickX((50, 30), (30, 50)).click_type)

    def test_str(self):
        test = click_x.ClickX((17, 39), "m")
        self.assertEqual("Middle click at (17, 39)", test.__str__())

        test2 = click_x.ClickX("bad data", 29)
        self.assertEqual("Left click at (0, 0)", test2.__str__())
