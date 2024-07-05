from unittest import TestCase
from actions import mouse_to
# from pynput.mouse import Controller



class TestMouseTo(TestCase):
    pass

    def test_coordinate_passing_valid_data(self):
        coords = (30, 50)
        assert coords, mouse_to.MouseTo(coords).coordinates

    def test_coordinates_passing_too_much_data(self):
        coords = (80, 70)
        assert coords, mouse_to.MouseTo((80, 70, 3)).coordinates
        assert coords, mouse_to.MouseTo((80, 70, "3")).coordinates

    def test_coordinate_passing_invalid_data(self):
        top_left = (0, 0)
        assert top_left, mouse_to.MouseTo(50).coordinates

        assert top_left, mouse_to.MouseTo(("300", "8000")).coordinates

    def test_str_method(self):
        assert "Mouse to (1390, 123)", mouse_to.MouseTo((1390, 123)).__str__()

        assert "Mouse to (0, 0)", mouse_to.MouseTo("should end up at (0, 0)").__str__()

    # Need to test the run function, undecided on how to do that as having the mouse be moved in testing isn't great
