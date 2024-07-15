from unittest import TestCase
from actions import swipe_xy


class TestSwipeXY(TestCase):

    def test_coordinate_passing_valid_data(self):
        start_coordinates = (30, 500)
        end_coordinates = (300, 200)
        self.assertEqual(start_coordinates, swipe_xy.SwipeXY(start_coordinates, start_coordinates).start)
        self.assertEqual(end_coordinates, swipe_xy.SwipeXY(start_coordinates, end_coordinates).end)

    def test_coordinates_passing_too_much_data(self):
        start_coordinates = (80, 70)
        end_coordinates = (2000, 1000)

        self.assertEqual(start_coordinates, swipe_xy.SwipeXY((80, 70, 8000), (30, 900)).start)
        self.assertEqual(start_coordinates, swipe_xy.SwipeXY((80, 70, "3"), (70, 100, 3000)).start)

        self.assertEqual(end_coordinates, swipe_xy.SwipeXY(start_coordinates, (2000, 1000, 901)).end)
        self.assertEqual(end_coordinates, swipe_xy.SwipeXY((3000, "30", 8), (2000, 1000, "cool number here")).end)

    def test_coordinate_passing_invalid_data(self):
        zero_zero = (0, 0)

        self.assertEqual(zero_zero, swipe_xy.SwipeXY(("x", "y"), (300, 100)).start)
        self.assertEqual(zero_zero, swipe_xy.SwipeXY(("x", "y"), ("x2, y2")).start)

        self.assertEqual(zero_zero, swipe_xy.SwipeXY((400, 300), ("x, y")).end)
        self.assertEqual(zero_zero, swipe_xy.SwipeXY(("x", "z"), ("x2, y2")).end)

    def test_coordinate_passing_partially_incorrect_data(self):
        good_coord = (900, 500)

        self.assertEqual(good_coord, swipe_xy.SwipeXY((900, 500), "no").start)

        self.assertEqual(good_coord, swipe_xy.SwipeXY("this is not what we want", good_coord).end)


    def test_str_method(self):
        self.assertEqual("Swipe between (300, 500) and (200, 100)",
                         swipe_xy.SwipeXY((300, 500), (200, 100)).__str__())
        self.assertEqual("Swipe between (1000, 2000) and (0, 0)",
                         swipe_xy.SwipeXY((1000, 2000), "bad").__str__())
        self.assertEqual("Swipe between (0, 0) and (0, 0)",
                         swipe_xy.SwipeXY("not", "correct").__str__())
