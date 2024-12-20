from misc_utilities import listener
from pynput.keyboard import Key, Listener, KeyCode
import pickle
from conditions import ImageCondition


macros = ["HI"]
hotkeys = ["f8", "a"]
listener = listener

for i in range(len(hotkeys)):
    listener.change_hotkey(hotkeys[i], i)


# def load_macros():
#     global macros
#     with open(file_name, 'rb') as f:
#         functions = pickle.load(f)

#     for i in range(len(functions[0])):


def load_macros(file_name):
    if file_name:
        with open(file_name, 'rb') as f:
            functions = pickle.load(f)

        base_length = len(self.actions)

        for i in range(len(functions[0])):
            # Recovering the Condition QPixmaps (they're set to None, so they can be pickled)
            [present_image.recover_pixmap() for present_image in functions[1][i]]
            [absent_image.recover_pixmap() for absent_image in functions[2][i]]

            self.macro_list.insertItem(len(self.actions), functions[5][i])
            self.actions.append(functions[0][i])
            self.present_images.append(functions[1][i])
            self.absent_images.append(functions[2][i])
            self.run_counts.append(functions[4][i])
            self.advanced_actions.append(functions[6][i])

            if functions[3][i] not in hotkeys:
                hotkeys.append(functions[3][i])
            else:
                hotkeys.append("")
            