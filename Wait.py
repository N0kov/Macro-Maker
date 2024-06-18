import time


class Wait:

    def __init__(self, wait_time):
        self.wait_time = wait_time

    def __str__(self):
        return "Waiting for " + str(self.wait_time) + " seconds"

    def run(self):
        time.sleep(self.wait_time)

# Ex:

# test = Wait(2.3)
# test.run()
# print(test)