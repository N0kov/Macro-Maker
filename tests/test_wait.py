from unittest import TestCase
from actions import Wait


class TestWait(TestCase):
    def test_wait_add(self):
        test = Wait(5)
        self.assertEqual(5, test.wait_time)

    def test_wait_str_method(self):
        self.assertEqual("Waiting for 3 seconds", Wait(3).__str__())

    def test_valid_input(self):
        self.assertEqual(0, Wait("aaa").wait_time)
        self.assertEqual(0, Wait(-3).wait_time)
        self.assertEqual(0, Wait(0).wait_time)

    def test_str(self):
        self.assertEqual("Waiting for 3 seconds", Wait(3).__str__())
        self.assertEqual("Waiting for 0 seconds", Wait(-20).__str__())
