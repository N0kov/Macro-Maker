import pickle
import Image
import Listener
from actions import ClickX, MouseTo, SwipeXY, TypeText, Wait


actions = []
present_images = []
absent_images = []


def main():

    choice = ""
    while choice != "q":
        choice = input(
            "What would you like to do? (S)wipe, (C)lick somewhere, (T)ype (M)ove mouse, (W)ait, (D)elete an action,"
            "\n(Cr)eate a condition, (Te)st the macro, (P)rint the actions or (L)oad from a file ").lower()

        if choice in ("s", "c", "t", "m", "w"):
            actions.append(make_action(choice))
        elif choice == "cr":
            add_image_condition()
        elif choice == "te":
            run_all()
        elif choice == "d":
            delete_action()
        elif choice == "p":
            print()
            print("Running these actions:")
            print(get_actions())
        elif choice == "l":
            load_from_pkl(input("Please input the pickle file location "))

        print()

        if choice in ("s", "c", "t", "m", "w") and len(actions) > 1:
            insert_at_index()
            print()

    save = input("Do you want to save the file? (y or yes) ").lower()
    if save == "y" or save == "yes":
        name = input("What do you want to name this? ")
        with open(name, 'wb') as f:
            pickle.dump([actions, present_images, absent_images], f)

    run_or_not = input("Run the macro? (y or yes) ").lower()
    if run_or_not == "y" or run_or_not == "yes":
        run_all()


def make_action(choice):
    if choice == "s":
        return SwipeXY()
    elif choice == "c":
        return ClickX()
    elif choice == "t":
        return TypeText()
    elif choice == "m":
        return MouseTo()
    elif choice == "w":
        return Wait()
    return None


def get_actions():
    if len(actions) > 0:
        message = "1) " + str(actions[0])
        for i in range(1, len(actions)):
            message += "\n" + str(i + 1) + ") " + str(actions[i])
        return message
    return ""


def add_image_condition():
    present = ''
    while present not in {"p", "a"}:
        present = input("Do you want the image to be (P)resent or (A)bsent? ").lower()
    if present == "p":
        present_images.append(Image.Image())
    else:
        absent_images.append(Image.Image())


def delete_action():
    if len(actions) > 1:
        print()
        print("Current actions:")
        print(get_actions())
        print()
        while True:
            index = input("Which item would you like to remove? ")
            try:
                if -1 < int(index) - 1 < len(actions):
                    print("Removing " + str(actions.pop(int(index) - 1)))
                    break
            except ValueError:
                pass
    elif len(actions) == 1:
        actions.pop()
    else:
        print("There needs to be at least one action present to delete an action")


def insert_at_index():
    new_object = actions.pop()
    print("Current commands'/home/lincolnm/Scripts/athing.pkl':\n" + get_actions() + " ")
    index = input("Please pick an index ")
    try:
        if -1 < int(index) - 1 < len(actions):
            actions.insert((int(index) - 1), new_object)
    except ValueError:
        actions.append(new_object)


def load_from_pkl(directory):
    try:
        with open(directory, 'rb') as f:
            functions = pickle.load(f)
        actions.extend(functions[0])
        present_images.extend(functions[1])
        absent_images.extend(functions[2])
    except FileNotFoundError:
        pass


def run_all():
    while True:
        if any(not image.run() for image in present_images) or any(
                image.run() for image in absent_images):
            continue
        break
    Listener.start_listener()
    for action in actions:
        if not Listener.continue_script():
            break
        action.run()


if __name__ == "__main__":
    main()
