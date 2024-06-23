from actions.action import Action
from pynput.keyboard import Key, Controller

keyboard = Controller()


class TypeText(Action):
    def __init__(self, phrase=None):
        if phrase == None:
            phrase = input("Enter the phrase you would like to type. Add \'+\' between keys for a function ")
        self.series = []
        if '+' not in phrase:
            self.series = list(phrase)
        else:
            self.setup_series(phrase)
            self.clean_input()

    def run(self):
        self.multi_input(0)

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

    def multi_input(self, i):
        if i < len(self.series) - 1:
            with keyboard.pressed(self.series[i]):
                i += 1
                self.multi_input(i)
        else:
            keyboard.press(self.series[i])
            keyboard.release(self.series[i])
