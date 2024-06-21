from actions.action import Action
from time import sleep


class Wait(Action):

    def __init__(self):
        while True:
            wait_time = input("How long would you like to wait for (in seconds)? ")
            try:
                wait_time = float(wait_time)
                if wait_time >= 0:
                    break
            except ValueError:
                pass
        self.wait_time = wait_time

    def __str__(self):
        return "Waiting for " + str(self.wait_time) + " seconds"

    def run(self):
        sleep(self.wait_time)
