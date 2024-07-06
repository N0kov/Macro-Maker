from unittest import TestCase
from actions import swipe_xy
# from pynput.mouse import Controller  # - again, need to figure out how to test run()



class TestSwipeXY(TestCase):

    def test_coordinate_passing_valid_data(self):
        start_coordinates = (30, 500)
        end_coordinates = (300, 200)
        assert start_coordinates, swipe_xy.SwipeXY(start_coordinates).start
        assert end_coordinates, swipe_xy.SwipeXY(end_coordinates).end

    def test_coordinates_passing_too_much_data(self):
        start_coordinates = (80, 70)
        end_coordinates = (2000, 1000)

        assert start_coordinates, swipe_xy.SwipeXY((80, 70, 8000)).start
        assert start_coordinates, swipe_xy.SwipeXY((80, 70, "3")).start

        assert end_coordinates, swipe_xy.SwipeXY((2000, 1000, 901)).end
        assert end_coordinates, swipe_xy.SwipeXY((2000, 1000, "cool number here")).end

    def test_coordinate_passing_invalid_data(self):
        zero_zero = (0, 0)

        assert zero_zero, swipe_xy.SwipeXY(50).start
        assert zero_zero, swipe_xy.SwipeXY(("x", "y"), (300, 100)).start
        assert zero_zero, swipe_xy.SwipeXY(("x", "y"), ("x2, y2")).start

        assert zero_zero, swipe_xy.SwipeXY(50).end
        assert zero_zero, swipe_xy.SwipeXY((400, 300), ("x, y")).end
        assert zero_zero, swipe_xy.SwipeXY(("x", a_number), ("x2, y2")).end

    def test_coordinate_passing_partially_incorrect_data(self):
        good_coord = (900, 500)

        assert good_coord, swipe_xy.SwipeXY((900, 500), bad_data).start

        assert good_coord, swipe_xy.SwipeXY((900, 500), "this is not what we want").end


    def test_str_method(self):
        assert "Swipe between (300, 500) and (200, 100)", swipe_xy.SwipeXY((300, 500), (200, 100)).__str__()
        assert "Swipe between (1000, 2000) and (0, 0)", swipe_xy.SwipeXY((1000, 2000)).__str__()
