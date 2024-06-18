from pyinput import get_mouse_positon
import pickle
import ClickX # Objects from here on
import Image
import Listener
import MouseTo
import SwipeXY
import Type
import Wait



class MainClass:
    def __init__(self):
        self.actions = []
        self.present_images = []
        self.absent_images = []
        choice = ""
        while choice != "q":
            choice = input("What would you like to do? (S)wipe, (C)lick somewhere, (T)ype (M)ove mouse, (Cr)eate a condition,"
                           + "\n(W)ait, (Te)st the macro, (D)elete the most recent action or (L)ist the actions ").lower()

            if choice == "s":
                print("Move your mouse to the desired start position. Press shift when ready. ", end="")
                Listener.start_listener()
                while Listener.continue_script():
                    pass
                x1, y1 = get_mouse_positon()
                print("\nMove your mouse to the desired end position. Press shift when ready. ", end="")
                Listener.start_listener()
                while Listener.continue_script():
                    pass
                x2, y2 = get_mouse_positon()
                self.actions.append(SwipeXY.SwipeXY((x1, y1), (x2, y2)))
                print()

            elif choice == "c":
                print("Move your mouse to the desired position. Press shift when ready. ", end="")
                Listener.start_listener()
                while Listener.continue_script():
                    pass
                x, y = get_mouse_positon()
                print()
                click_type = ""
                while click_type != "l" and click_type != "r" and click_type != "m":
                    click_type = input("(L)eft, (R)ight or (M)iddle click? ").lower()
                self.actions.append(ClickX.ClickX(x, y, click_type))

            elif choice == "t":
                text = input("Enter the phrase you would like to type. Add \'+\' between keys for a function ")
                self.actions.append(Type.Type(text))

            elif choice == "m":
                print("Move your mouse to the desired position. Press shift when ready. ", end="")
                Listener.start_listener()
                while Listener.continue_script():
                    pass
                self.actions.append(MouseTo.MouseTo(get_mouse_positon()[0], get_mouse_positon()[1]))
                print()

            elif choice == "cr":
                present = ''
                while present != "p" and present != "a":
                    present = input("Do you want the image to be (P)resent or (A)bsent? ").lower()
                print("Move your mouse to the top left of the image. Press shift when ready. ", end="")
                Listener.start_listener()
                while Listener.continue_script():
                    pass
                x1, y1 = get_mouse_positon()
                print("\nMove your mouse to the bottom right of the image. Press shift when ready. ", end="")
                Listener.start_listener()
                while Listener.continue_script():
                    pass
                x2, y2 = get_mouse_positon()
                print()
                if (present == "p"):
                    self.present_images.append(Image.Image([x1, y1], [x2, y2]))
                else:
                    self.absent_images.append(Image.Image([x1, y1], [x2, y2]))

            elif choice == "w":
                while True:
                    wait_time = input("How long would you like to wait for (in seconds)? ")
                    try:
                        wait_time = float(wait_time)
                        if wait_time >= 0:
                            break
                    except ValueError:
                        pass
                self.actions.append(Wait.Wait(wait_time))

            elif choice == "te":
                self.run_all()

            elif choice == "d":
                if len(self.actions) > 0:
                    self.actions.pop()
                else:
                    print("There needs to be at least one action added to do this")

            elif choice == "l":
                print()
                print(self.__str__())

            print()

        save = input("Do you want to save the file? (y or yes) ").lower()
        if save == "y" or save == "yes":
            name = input("What do you want to name this? ")
            with open(name, 'wb') as f:
                pickle.dump([self.actions, self.present_images, self.absent_images], f)

        run_or_not = input("Run the macro? (y or yes) ").lower()
        if run_or_not == "y" or run_or_not == "yes":
            self.run_all()
            print("done")


    def __str__(self):
        message = "Running these actions:"
        for action in self.actions:
            message += "\n" + action.__str__()
        return message

    def run_all(self):
        while True:
            if not (not any(not image.run() for image in self.present_images) and not any(
                    image.run() for image in self.absent_images)):
                continue
            break
                Listener.start_listener()
        for action in self.actions:
            if not Listener.continue_script():
                break
            action.run()

    def import_commands(self, actions, present_images, absent_images):
        self.actions += actions
        self.present_images += present_images
        self.absent_images += absent_images

    def load_and_run(self, directory):
        with open(directory, 'rb') as f:
            functions = pickle.load(f)
        self.import_commands(functions[0], functions[1], functions[2])
        self.run_all()

    def print_actions(self):
        for action in self.actions:
            print(action, end = " ")



if __name__ == "__main__":
    thing = MainClass()
