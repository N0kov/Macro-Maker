from pyinput import get_mouse_positon
import listener
import ClickX
import MouseTo
import Type
import SwipeXY

class Main:
    def __init__(self):
        self.actions = []
        choice = ""
        while choice != "q":
            choice = input("What would you like to do? (S)wipe, (C)lick somewhere, (T)ype (M)ove mouse ")
            if choice == "S":
                print("Move your mouse to the desired start position. Press shift when ready. ", end="")
                listener.start_listener()
                while listener.continue_script():
                    pass
                x1, y1 = get_mouse_positon()
                print("\nMove your mouse to the desired end position. Press shift when ready. ", end="")
                listener.start_listener()
                while listener.continue_script():
                    pass
                x2, y2 = get_mouse_positon()
                self.actions.append(SwipeXY.SwipeXY((x1, y1), (x2, y2)))
                print()

            elif choice.lower() == "c":
                print("Move your mouse to the desired position. Press shift when ready. ", end="")
                listener.start_listener()
                while listener.continue_script():
                    pass
                self.actions.append(ClickX.ClickX(get_mouse_positon()[0], get_mouse_positon()[1]))
                print()

            elif choice.lower() == "t":
                text = input("Enter the phrase you would like to type. If you want a function, use \"+\" (e.g. \"ctrl+v\" or \"down+\") ")
                self.actions.append(Type.Type(text))

            elif choice.lower() == "m":
                print("Move your mouse to the desired position. Press shift when ready. ", end="")
                listener.start_listener()
                while listener.continue_script():
                    pass
                self.actions.append(MouseTo.MouseTo(get_mouse_positon()[0], get_mouse_positon()[1]))
                print()

    def run_all(self):
        for i in range(len(self.actions)):
            current = self.actions[i]
            current.run()


thing = Main()

thing.run_all()

