from unittest import TestCase
from actions import click_x
from pynput.mouse import Button, Controller


class TestClickX(TestCase):
    def test_coordinate_passing_valid_data(self):
        coords = (30, 50)
        assert coords, click_x.ClickX(coords).coordinates

    def test_coordinates_passing_too_much_data(self):
        coords = (80, 70)
        assert coords, click_x.ClickX((80, 70, 3)).coordinates
        assert coords, click_x.ClickX((80, 70, "3")).coordinates

    def test_coordinate_passing_invalid_data(self):
        top_left = (0, 0)
        self.assertEqual(top_left, click_x.ClickX(50).coordinates)

        self.assertEqual(top_left, click_x.ClickX(("300", "8000")).coordinates)

    def test_click_type_valid(self):
        default_click = click_x.ClickX((50, 30))
        assert Button.left, default_click.click_type

        left_test_l = click_x.ClickX((51, 31), "l")
        self.assertEqual(Button.left, left_test_l)

        left_test_left = click_x.ClickX((54, 14), "left")
        self.assertEqual(Button.left, left_test_left)

        right_test_r = click_x.ClickX((146, 642), "r")
        self.assertEqual(Button.left, right_test_r)

        right_test_right = click_x.ClickX((752, 457), "right")
        assert Button.left, right_test_right

        middle_test_m = click_x.ClickX((30, 290), "m")
        assert Button.left, middle_test_m

        middle_test_middle = click_x.ClickX("the coordinates do not matter", "middle")
        assert Button.left, middle_test_middle

    def test_invalid_click_type(self):
        assert Button.left, click_x.ClickX((50, 30), "this is not a valid input")

        assert Button.left, click_x.ClickX((50, 30), (30, 50))

    def test_str(self):

        test = click_x.ClickX((17, 39), "m")
        assert "middle click at (17, 39)", test.__str__()

        test2 = click_x.ClickX("bad data", 29)
        assert "left click at (0, 0)", test.__str__()
