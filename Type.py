from pyinput import multi_input
from pynput.keyboard import Key
import time


class Type:
    def __init__(self, phrase):
        self.series = []
        if '+' not in phrase:
            self.series = list(phrase)
        else:
            self.setup_series(phrase)
            self.clean_input()


    def run(self):
        multi_input(self.series, 0)
        time.sleep(.1)

    def __str__(self):
        if self.series:
            return "Typing: " + ", ".join(map(str, self.series))
        return ""

    def setup_series(self, phrase):
        while len(phrase) != 0:
            if '+' in phrase:
                self.series.append(phrase[:phrase.find('+')])
                phrase = phrase[phrase.find('+') + 1:]
            else:
                self.series.append(phrase)
                phrase = ''

    def clean_input(self):
        modifier_keys = ["ctrl", "alt", "shift", "cmd"]
        temp_series = [] + self.series
        self.series.clear()

        for i in range(len(temp_series)):
            if len(temp_series[i]) > 1:
                if temp_series[i] in modifier_keys:
                    self.series.insert(0, getattr(Key, (temp_series[i])))
                else:
                    self.series.append(getattr(Key, (temp_series[i])))
            else:
                self.series.append(temp_series[i])


# Test code (should write Hello World!, copy it, paste it below and then alt+tab
#            Inconsistent formating between commands and key inputs intentionally):

# hello = Type("Hello World!")
# shift_up = Type("shift+up")
# right = Type("right+")
# shift_right = Type("shift+right")
# copy = Type("ctrl+c")
# down = Type("down+")
# paste = Type("v+ctrl")
# atab = Type("tab+alt")

# print(hello)
# print(atab)

# hello.run()
# shift_up.run()
# shift_right.run()
# copy.run()
# down.run()
# paste.run()