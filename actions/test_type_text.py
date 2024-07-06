from unittest import TestCase
from actions import type_text
from pynput.keyboard import Key


class TestTypeText(TestCase):

    def test_string(self):
        test_1_list = ["a", "b", "c"]
        self.assertEqual(test_1_list, type_text.TypeText("abc").series)

        test_2_list = ["H", "e", "l", "l", "o", " ", "W", "o", "r", "l", "d", "!"]
        self.assertEqual(test_2_list, type_text.TypeText("Hello World!").series)

    def test_string_with_plus(self):  # An additional \ is required to be able to input this via code
        test_1_list = ["a", "b", "+", "+"]
        self.assertEqual(test_1_list, type_text.TypeText("ab\\+\\+").series) # Only use one \ in the UI

        test_2_list = ["+"]
        self.assertEqual(test_2_list, type_text.TypeText("\\+").series)

        test_3_list = ["a", "+", "b"]
        self.assertEqual(test_3_list, type_text.TypeText("a\\+b").series)

        test_4_list = ["+", "a"]
        self.assertEqual(test_4_list, type_text.TypeText("\\+a").series)

        test_5_list = ["H", "e", "l", "l", "o", "+", "W", "o", "r", "l", "d", "+", "!", "+"]
        self.assertEqual(test_5_list, type_text.TypeText("Hello\\+World\\+!\\+").series)

    def test_command(self):
        ctrl = getattr(Key, "ctrl") # Just using three commands, the rest function the same
        shift = getattr(Key, "shift")
        up = getattr(Key, "up")

        ctrl_v = [ctrl, "v"]
        self.assertEqual(ctrl_v, type_text.TypeText("ctrl+v").series)  # They're stored as lists, so it's fine doing it like this
        self.assertEqual(ctrl_v, type_text.TypeText("v+ctrl").series)  # Should reformat so that commands are at the front

        shift_up = [shift, up]
        self.assertEqual(shift_up, type_text.TypeText("shift+up").series)  # Should have up right down left be after other modifiers
        self.assertEqual(shift_up, type_text.TypeText("up+shift").series)

        assert getattr(Key, "cmd_l"), type_text.TypeText("cmd_l+")

    def test_bad_command(self):
        bad_hello = ["H", "e", "l", "l", "o"]
        self.assertEqual(bad_hello, type_text.TypeText("Hel+lo").series)

        test_phrase = [getattr(Key, "alt"), "u", "p", "u"]
        self.assertEqual(test_phrase, type_text.TypeText("alt+upu").series)

    def test_str(self):
        hello_world_str = "Typing: H, e, l, l, o, +, W, o, r, l, d, +, !, +"
        self.assertEqual(hello_world_str, type_text.TypeText("Hello\\+World\\+!\\+").__str__())

        self.assertEqual("Typing: Key.shift, Key.up", type_text.TypeText("shift+up").__str__())
