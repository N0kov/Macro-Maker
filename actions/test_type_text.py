from unittest import TestCase
from actions import type_text
from pynput.keyboard import Key


class TestTypeText(TestCase):

    def test_string(self):
        assert "a, b, c", type_text.TypeText("abc")
        assert "H, e, l, l, o,  , W, o, r, l, d, !", type_text.TypeText("Hello World!")

    def test_string_with_plus(self):  # An additional \ is required to be able to input this via code
        assert "a, b, +, +", type_text.TypeText("ab\\+\\+") # Only use one \ in the UI
        assert "+", type_text.TypeText("\\+")
        assert "a, +, b", type_text.TypeTextUI("a\\+b")
        assert "+, a", type_text.TypeText("\\+a")
        assert "H, e, l, l, o, +, W, o, r, l, d, +, !, +", type_text.TypeText("Hello\\+World\\+!\\+")

    def test_command(self):
        ctrl = getattr(Key, "ctrl") # Just using three commands, the rest function the same
        shift = getattr(Key, "shift")
        up = getattr(Key, "up")

        ctrl_v = {ctrl, "v"}
        assert ctrl_v, type_text.TypeText("ctrl+v")  # They're stored as lists, so it's fine doing it like this
        assert ctrl_v, type_text.TypeText("v+ctrl")  # Should reformat so that commands are at the front

        shift_up = {shift, up}
        assert shift_up, type_text.TypeText("shift+up")  # Should have up right down left be after other modifiers
        assert shift_up, type_text.TypeText("up+shift")

        assert getattr(Key, "cmd_l"), type_text.TypeText("cmd_l+")

    def test_bad_command(self):
        assert "H, e, l, l, o", type_text.TypeText("Hel+lo")

        test_phrase = {getattr(Key, "alt"), "upu"}
        assert test_phrase, type_text.TypeText("alt+upu")

    def test_str(self):
        assert "Typing: H, e, l, l, o, +, W, o, r, l, d, +, !, +", type_text.TypeText("Hello\\+World\\+!\\+").__str__()

        assert "Typing: Key.shift, Key.up", type_text.TypeText("shift+up").__str__()
