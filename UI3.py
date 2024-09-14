import _pickle
import pickle
import queue
import threading
import sys

import inflect
import word2number.w2n as w2n
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import *

from actions import *
from conditions.ImageCondition import *
from misc_utilities import *
from ui_files import *


class MacroManagerMain(QMainWindow):
    """
    The main application for Macro-Maker. This manages the main GUI, holds the action and condition classes, allows
    scripts to run and call on the other classes
    """
    def __init__(self):
        super().__init__()
        self.actions = [[]]
        self.present_images = [[]]
        self.absent_images = [[]]
        self.advanced_actions = [[]]
        self.hotkeys = ["f8"]
        self.run_counts = [1]
        listener.change_hotkey(self.hotkeys[0], 0)
        self.current_macro = 0
        self.macros_to_run = queue.Queue()
        self.mutex = threading.Lock()
        self.current_running_macro = 0
        # This one is so weighty that it needs this so that the delay isn't too bad on going to the view
        self.image_config_view = ImageConditionUI(self)

        self.start_hotkey_listener()  # Thread stuff - checking for the hotkey to run your script
        self.run_action_condition = threading.Condition()  # Notification for the thread that runs the macro
        self.start_action_thread()  # Thread that runs the macro
        self.running_macro = False  # Bool for if the macro is running or not

        self.setWindowTitle("Macro Manager")
        self.setGeometry(400, 200, 1100, 700)

        self.central_widget = QStackedWidgetCleaner(self)
        self.setCentralWidget(self.central_widget)

        self.main_view = QWidget()
        self.main_layout = QVBoxLayout(self.main_view)

        self.init_top_ui()
        self.init_action_condition_ui()
        self.update_condition_list()

    def init_top_ui(self):
        """
        Initializes the top section of the UI where the buttons are for running, changing the run count, etc.
        """
        top_layout = QHBoxLayout()
        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        save_button = QAction("Save", self)
        load_button = QAction("Load", self)
        save_button.triggered.connect(self.save_macros)
        load_button.triggered.connect(self.load_macros)

        file_menu.addAction(save_button)
        file_menu.addAction(load_button)

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.notify_action_thread)

        self.run_options = QComboBox()
        self.run_options.addItem("Run once")
        self.run_options.addItem("Run infinitely")
        self.run_options.addItem("Custom run count")
        self.run_options.currentIndexChanged.connect(self.run_options_clicked)

        self.set_hotkey_button = QPushButton("Set a hotkey (currently " + str(self.hotkeys[0]) + ")")
        self.set_hotkey_button.clicked.connect(self.hotkey_clicked)

        self.macro_list = QComboBox()
        self.macro_list.addItem("Macro one")
        self.macro_list.addItem("Create a macro")
        self.macro_list.addItem("Rename a macro")
        self.macro_list.currentIndexChanged.connect(self.switch_macro)
        self.current_macro = 0  # Not strictly needed but writing self.macro_list.currentIndex() everywhere
        # is very clunky

        meta_modifier_button = QPushButton("Set meta modifiers")
        meta_modifier_button.clicked.connect(self.switch_to_meta_modifier_view)

        top_layout.addWidget(self.run_button)
        top_layout.addWidget(self.run_options)
        top_layout.addWidget(self.set_hotkey_button)
        top_layout.addWidget(self.macro_list)
        top_layout.addWidget(meta_modifier_button)
        self.main_layout.addLayout(top_layout)

    def init_action_condition_ui(self):
        """
        Initializes the main section of the UI where the actions and conditions are
        """
        middle_layout = QHBoxLayout()

        actions_frame = QFrame(self)  # Actions start here
        actions_frame.setFrameShape(QFrame.Shape.StyledPanel)
        actions_layout = QVBoxLayout(actions_frame)
        actions_label = QLabel("Actions")

        self.action_list = CustomDraggableList(self, self.actions)

        actions_layout.addWidget(actions_label)
        actions_layout.addWidget(self.action_list)

        self.meta_modifier_run_type = QLabel("")
        meta_modifier_box = QVBoxLayout()
        self.advanced_action_list = CustomDraggableList(self, self.advanced_actions)
        meta_modifier_box.addWidget(self.advanced_action_list)
        meta_modifier_box.setContentsMargins(0, 0, 0, 0)

        self.meta_modifier_widget = QWidget()
        self.meta_modifier_widget.setLayout(meta_modifier_box)
        actions_layout.addWidget(self.meta_modifier_run_type)
        actions_layout.addWidget(self.meta_modifier_widget)

        self.meta_modifier_run_type.hide()
        self.meta_modifier_widget.hide()

        actions_layout.addWidget(self.meta_modifier_widget)

        add_action_button = create_push_button()
        add_action_button.clicked.connect(lambda: self.switch_to_add_action_view("main_app"))
        actions_layout.addWidget(add_action_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight |
                                                              QtCore.Qt.AlignmentFlag.AlignBottom)

        middle_layout.addWidget(actions_frame)

        conditions_frame = QFrame(self)
        conditions_frame.setFrameShape(QFrame.Shape.StyledPanel)
        conditions_layout = QVBoxLayout(conditions_frame)
        conditions_layout.setContentsMargins(0, 7, 0, 8)
        conditions_layout.setSpacing(0)

        # For some reason these two labels are 7 pixels too far to the left versus the actions label, so they need
        # to be moved. The same minor pixel movements go for the above context margins and the hbox for the + button
        present_label_right_mover_hbox = QHBoxLayout()
        absent_label_right_mover_hbox = QHBoxLayout()
        present_label_right_mover_hbox.setContentsMargins(8, 0, 0, 0)
        absent_label_right_mover_hbox.setContentsMargins(8, 0, 0, 0)
        present_label = QLabel("Present images")
        absent_label = QLabel("Absent images")
        present_label_right_mover_hbox.addWidget(present_label)
        absent_label_right_mover_hbox.addWidget(absent_label)

        present_container = QVBoxLayout()
        absent_container = QVBoxLayout()

        p_grid_scroll_area = QScrollArea(self)
        p_grid_scroll_area.setWidgetResizable(True)
        self.p_grid_widget = QWidget()
        self.p_image_grid = QGridLayout(self.p_grid_widget)
        p_grid_scroll_area.setWidget(self.p_grid_widget)

        a_grid_scroll_area = QScrollArea(self)
        a_grid_scroll_area.setWidgetResizable(True)
        a_grid_widget = QWidget()
        self.a_image_grid = QGridLayout(a_grid_widget)
        a_grid_scroll_area.setWidget(a_grid_widget)

        self.image_dimensions = 150
        for condition_type in (self.p_image_grid, self.a_image_grid):
            condition_type.setVerticalSpacing(7)
            condition_type.setHorizontalSpacing(8)

        present_container.addWidget(p_grid_scroll_area)
        absent_container.addWidget(a_grid_scroll_area)

        present_widget = QWidget()
        conditions_layout.addLayout(present_label_right_mover_hbox)
        present_widget.setLayout(present_container)
        conditions_layout.addWidget(present_widget)

        conditions_layout.addLayout(absent_label_right_mover_hbox)
        absent_widget = QWidget()
        absent_widget.setLayout(absent_container)
        conditions_layout.addWidget(absent_widget)

        condition_button = create_push_button()
        condition_button.clicked.connect(self.switch_to_add_condition_view)

        hbox_to_move_plus_button_left = QHBoxLayout()
        hbox_to_move_plus_button_left.setContentsMargins(0, 0, 10, 0)
        hbox_to_move_plus_button_left.addWidget(condition_button,
                                                alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        conditions_layout.addLayout(hbox_to_move_plus_button_left)

        middle_layout.addWidget(conditions_frame)

        self.main_layout.addLayout(middle_layout)
        self.central_widget.addWidget(self.main_view)
        self.central_widget.setCurrentWidget(self.main_view)

    def run_macro(self, macro):
        """
        The main script to run the macro. It checks for if all the image conditions are present / absent, then runs
        the actions. Triggered from the run button or pressing the hotkey. Killed on pressing the hotkey as well
        Runs on action_thread, all internal definitions will also quit on hotkey press
        run_count being set to -1 means that it will run infinitely. Otherwise, the macro will run equal to the
        amount of times listed
        """
        if not self.actions:  # So processing power isn't wasted running a script that will trigger nothing
            return

        if self.run_counts[macro] > 0:
            [self.run_loop(macro) for _ in range(self.run_counts[macro]) if self.running_macro]

        else:
            while self.running_macro:
                self.run_loop(macro)

    def advanced_run_macro(self, macro):
        if self.advanced_actions[macro][0] > 0:
            [self.run_loop(macro) for _ in range(self.advanced_actions[macro][0]) if self.running_macro]
            [action.run() for action in self.advanced_actions[macro][1] if self.running_macro]
        else:
            while self.running_macro:
                if self.check_images_advanced(macro):
                    [action.run() for action in self.actions[macro] if self.running_macro]
                else:
                    [action.run() for action in self.advanced_actions[macro][1] if self.running_macro]
                    break

    def run_loop(self, macro):
        """
        The default loop to be used to check for images and then run the actions
        Stops if the hotkey is pressed
        :param macro: The index of the macro to run
        """
        self.check_images(macro)
        [action.run() for action in self.actions[macro] if self.running_macro]

    def check_images(self, macro):
        """
        Checks all images in the specified macro to make sure that they are satisfied, then returns
        Stops if the hotkey is pressed
        :param macro: The index of the macro to run
        """
        while self.running_macro:
            if all(image.run() for image in self.present_images[macro]) and all(
                    not image.run() for image in self.absent_images[macro]):
                return

    def check_images_advanced(self, macro):
        for _ in range(-self.advanced_actions[macro][0]):
            if all(image.run() for image in self.present_images[macro]) and all(
                    not image.run() for image in self.absent_images[macro]):
                return True
        return False

    def run_options_clicked(self, option):
        """
        Processes when the run count dropdown is clicked. If run once or infinite is clicked, sets run_count to 1 or -1
        When Run x times is clicked, opens run_count_popup, sets run_count to the number selected and creates a new
        option for it, or resets back to before if cancel is hit
        This only accepts positive integers
        :param option: The option that the user clicked on from the dropdown menu of run counts
        """
        if self.run_options.itemText(option) != "Custom run count":
            self.set_run_count_from_run_options()
        else:
            popup = RunCountPopup()
            if popup.exec() == QDialog.DialogCode.Accepted:
                self.run_counts[self.current_macro] = popup.runs
            self.set_run_options_from_run_counts()

    def set_run_count_from_run_options(self):
        """
        Sets the current macro's run count (in run_counts) to whatever item is selected from run_options
        """
        if self.run_options.currentText() == "Run once":
            self.run_counts[self.current_macro] = 1
        elif self.run_options.currentText() == "Run infinitely":
            self.run_counts[self.current_macro] = -1
        elif len(self.run_options) == 4 and self.run_options.currentIndex() == 1:
            run_count_string = self.run_options.currentText().split()[1]
            self.run_counts[self.current_macro] = w2n.word_to_num(run_count_string)

    def set_run_options_from_run_counts(self):
        """
        Sets run_options to display the amount of times that the macro should run based on the current macro's run
        count (in run_counts)
        """
        self.run_options.blockSignals(True)

        if self.run_counts[self.current_macro] == -1:
            if self.run_options.count() == 4:
                self.run_options.setCurrentIndex(2)
            else:
                self.run_options.setCurrentIndex(1)
        elif self.run_counts[self.current_macro] == 1:
            self.run_options.setCurrentIndex(0)
        else:
            if self.run_options.count() == 3:
                self.run_options.insertItem(1, "")
            self.run_options.setItemText(1, "Run " +
                                         inflect.engine().number_to_words(self.run_counts[self.current_macro]) +
                                         " times")
            self.run_options.setCurrentIndex(1)
        self.run_options.blockSignals(False)

    def switch_macro(self):
        """
        Allows the user to switch to a different action / create one / remove a macro. Macros are only removable when
        there are at least two present
        """
        self.central_widget.cleanup_widgets()

        if self.macro_list.currentText() == "Create a macro":
            self.create_new_macro()

        elif self.macro_list.currentText() == "Remove a macro":
            self.remove_macro()

        elif self.macro_list.currentText() == "Rename a macro":
            popup = RenameMacroPopup(self.macro_list)
            if popup.exec() == QDialog.DialogCode.Accepted:
                self.macro_list.setItemText(popup.get_macro_choice(), popup.get_new_name())
                self.current_macro = popup.get_macro_choice()
                self.macro_list.setCurrentIndex(popup.get_macro_choice())
            else:
                self.macro_list.setCurrentIndex(0)

        else:
            self.current_macro = self.macro_list.currentIndex()
            self.set_run_options_from_run_counts()
            if self.hotkeys[self.current_macro] != "":
                self.set_hotkey_button.setText("Set a hotkey (currently " +
                                               str(self.hotkeys[self.current_macro]) + ")")
            else:
                self.set_hotkey_button.setText("Set a hotkey")

        self.update_action_list()
        self.update_condition_list()
        self.update_advanced_action_list()

    def create_new_macro(self):
        """
        Adds a new macro to the macro list, and empty sets of all the data associated with a macro
        """
        self.macro_list.blockSignals(True)
        if self.macro_list.itemText(self.macro_list.count() - 1) != "Remove a macro":
            self.macro_list.addItem("Remove a macro")

        macro_position = len(self.actions)
        self.macro_list.insertItem(macro_position, "Macro " +
                                   inflect.engine().number_to_words((macro_position + 1)))
        self.current_macro = macro_position
        self.macro_list.setCurrentIndex(macro_position)
        self.macro_list.blockSignals(False)

        self.actions.append([])
        self.present_images.append([])
        self.absent_images.append([])
        self.advanced_actions.append([])

        self.run_options.blockSignals(True)
        if self.run_options.count() == 4:
            self.run_options.removeItem(1)
        self.run_options.setCurrentIndex(0)
        self.run_options.blockSignals(False)

        self.run_counts.append(1)
        self.hotkeys.append("")
        listener.change_hotkey(self.hotkeys[self.current_macro], self.current_macro)
        self.set_hotkey_button.setText("Set a hotkey")

    def remove_macro(self):
        """
        Opens a popup that allows the user to pick a macro that they'd like to remove,
        then removes it and all of its fields
        """
        popup = RemoveMacroPopup(self.macro_list)
        if popup.exec() == QDialog.DialogCode.Accepted:
            self.macro_list.blockSignals(True)
            removal_index = popup.get_macro_to_remove()
            self.macro_list.removeItem(removal_index)
            self.hotkeys.pop(removal_index)
            self.actions.pop(removal_index)
            self.advanced_actions.pop(removal_index)
            self.present_images.pop(removal_index)
            self.absent_images.pop(removal_index)
            listener.remove_hotkey(removal_index)

            self.current_macro = 0

            self.fix_macro_list_names()
            self.update_trigger_macros(self.actions, removal_index)
            self.update_trigger_macros(self.advanced_actions, removal_index)
            self.update_action_list()
            self.update_advanced_action_list()

            self.macro_list.blockSignals(False)

        self.macro_list.setCurrentIndex(0)  # This is effectively recalling switch_macro and going to the else block

    def fix_macro_list_names(self):
        """
        Checks if the user has made a custom macro name, if so leaves it alone.
        If not, it renames it to be Macro + its index.
        Additionally, adds the remove a macro option if there are at least two macros present, removes it otherwise
        """
        for i in range(len(self.actions)):
            try:
                w2n.word_to_num(self.macro_list.itemText(i).split()[1])  # Custom macro == word two isn't a number
                self.macro_list.setItemText(i, ("Macro " + inflect.engine().number_to_words(i + 1)))
            except (ValueError, IndexError):
                pass

        try:
            if self.macro_list.count() == 4 and self.macro_list.itemText(3) == "Remove a macro":
                self.macro_list.removeItem(3)
            else:
                if self.macro_list.itemText(self.macro_list.count() - 1) != "Remove a macro":
                    self.macro_list.addItem("Remove a macro")
        except IndexError:
            pass

    def update_trigger_macros(self, action_list, removal_index):
        for i in range(len(action_list)):
            sublist = []
            if action_list is self.advanced_actions:
                try:
                    if action_list[i][1]:
                        sublist = action_list[i][1]
                except IndexError:
                    continue
            else:
                sublist = action_list[i]

            for j in range(len(sublist) - 1, -1, -1):
                if type(sublist[j]) is TriggerMacro:
                    if removal_index == sublist[j].get_index:
                        sublist.pop(j)
                    elif removal_index < sublist[j].get_index:
                        sublist[j].update_fields(-1, self.macro_list.itemText(sublist[j].get_index - 1))

    def hotkey_clicked(self):
        """
        Logic for if the change start / stop button is clicked. Opens hotkey_popup and allows the user to set a new
        hotkey. The button is updated after with the new hotkey. If the user gives no input or an invalid input,
        the hotkey will be set to none
        """
        popup = HotkeyPopup(self.current_macro, self.hotkeys)
        if popup.exec() == QDialog.DialogCode.Accepted:
            try:
                if list is type(popup.key_combination):
                    self.hotkeys[self.current_macro] = popup.key_combination[0]
                else:
                    self.hotkeys[self.current_macro] = popup.key_combination
                if self.hotkeys[self.current_macro] != "":
                    self.set_hotkey_button.setText("Set a hotkey (currently " +
                                                   str(self.hotkeys[self.current_macro]) + ")")
                else:
                    self.set_hotkey_button.setText("Set a hotkey")
            except (AttributeError, IndexError):
                self.hotkeys[self.current_macro] = ""
                self.set_hotkey_button.setText("Set a hotkey")
            listener.change_hotkey(self.hotkeys[self.current_macro], self.current_macro)

    def save_macros(self):
        """
        Saves the actions, conditions and hotkeys as a pickle file with a basic GUI file explorer dialogue
        """
        options = QFileDialog.Option(0)
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Macro", "",
                                                   "All Files (*);;Pickle Files (*.pkl)", options=options)
        if file_name:
            # The issue is that ImageConditions have a QPixmap inside of them (used to display the captured images
            # in the GUI). QPixmaps cannot be pickled, so this is setting all QPixmaps to None, and then recovering
            # them afterward. MacroManagerMain objects also can't be pickled, and the reference is needed
            # in TriggerMacro, so it also has to be removed
            for i in range(len(self.actions)):
                [self.absent_images[i][j].clear_pixmap() for j in range(len(self.absent_images[i]))]
                [self.present_images[i][j].clear_pixmap() for j in range(len(self.present_images[i]))]

            macro_name_list = []  # QComboBoxes can't be pickled either
            [macro_name_list.append(self.macro_list.itemText(i)) for i in range(len(self.actions))]

            with open(file_name, 'wb') as f:
                pickle.dump([self.actions, self.present_images, self.absent_images,
                             self.hotkeys, self.run_counts, macro_name_list, self.advanced_actions], f)

            for i in range(len(self.actions)):
                [self.absent_images[i][j].recover_pixmap() for j in range(len(self.absent_images[i]))]
                [self.present_images[i][j].recover_pixmap() for j in range(len(self.present_images[i]))]

    def load_macros(self):
        """
        Loads the actions and conditions from a specified file in a GUI dialogue. This must be a pickle file, if
        not it will just pass. This extends the preexisting actions, present_images and absent_images lists, so
        any actions and / or conditions that are already be present will stay at the front
        """
        options = QFileDialog.Option(0)
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Actions", "",
                                                   "All Files (*);;Pickle Files (*.pkl)", options=options)
        try:
            if file_name:
                with open(file_name, 'rb') as f:
                    functions = pickle.load(f)

                self.macro_list.blockSignals(True)
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

                    if functions[3][i] not in self.hotkeys:
                        self.hotkeys.append(functions[3][i])
                    else:
                        self.hotkeys.append("")
                    listener.change_hotkey(self.hotkeys[-1], (len(self.macro_list)))

                self.current_macro = len(self.actions) - 1
                self.macro_list.setCurrentIndex(self.current_macro)
                self.fix_macro_list_names()

                for i in range(base_length, len(self.actions)):
                    for action in self.actions[i]:
                        if type(action) is TriggerMacro:
                            action.update_fields(base_length, self.macro_list.itemText(
                                base_length + action.get_index))

                for i in range(base_length, len(self.advanced_actions)):
                    try:
                        for action in self.advanced_actions[i][1]:
                            if type(action) is TriggerMacro:
                                action.update_fields(base_length, self.macro_list.itemText(
                                    base_length + action.get_index))
                    except IndexError:
                        pass

                if self.hotkeys[self.current_macro] != "":
                    self.set_hotkey_button.setText("Set a hotkey (currently " +
                                                   str(self.hotkeys[self.current_macro]) + ")")
                else:
                    self.set_hotkey_button.setText("Set a hotkey")

                self.set_run_options_from_run_counts()
                self.update_condition_list()
                self.update_action_list()
                self.update_advanced_action_list()

                self.macro_list.blockSignals(False)

        except (_pickle.UnpicklingError, EOFError):  # If you click on a non-pickle file / a corrupt pkl file
            pass

    def save_meta_modifiers(self, count, actions_list):
        self.advanced_actions[self.current_macro] = [count, actions_list.copy()]

        self.update_advanced_action_list()

    def switch_to_meta_modifier_view(self):
        advanced_view = AdvancedActions(self, self.advanced_actions[self.current_macro])

        self.central_widget.addWidget(advanced_view)
        self.central_widget.setCurrentWidget(advanced_view)

    def update_advanced_action_list(self):
        """
        Refreshes the action list with all actions in actions so that all actions are visible to the user
        """
        self.advanced_action_list.clear()
        try:
            advanced_list = self.advanced_actions[self.current_macro]
            for action in advanced_list[1]:
                item = QListWidgetItem(str(action))
                item.setData(QtCore.Qt.ItemDataRole.UserRole, action)
                self.advanced_action_list.addItem(item)

            if advanced_list[0] > 0:
                meta_label_text = ("After running " +
                                   inflect.engine().number_to_words(advanced_list[0]) + " times:")
            else:
                meta_label_text = ("After failing to detect images " +
                                   inflect.engine().number_to_words(-advanced_list[0]) + " times:")

            self.meta_modifier_run_type.setText(meta_label_text)
            self.meta_modifier_run_type.show()
            self.meta_modifier_widget.show()

        except IndexError:
            self.meta_modifier_run_type.hide()
            self.meta_modifier_widget.hide()

    def switch_to_add_action_view(self, sender):
        """
        Called from the + button in the actions side
        The base UI for picking a new action to be made. Allows the user to pick an action from a list, and then
        opens the screen for said action. Also includes a back button if they decide to not add an action
        """
        action_config_view = self.generate_action_list(sender)

        self.central_widget.addWidget(action_config_view)
        self.central_widget.setCurrentWidget(action_config_view)

    def generate_action_list(self, sender):
        """
        Generates a QWidget that has a box containing all the possible actions. If the main app is the sender,
        a back button will also be created
        :param sender: The app that wants to run this - send self (not needed if from MMM)
        """
        action_config_view = QWidget()
        action_layout = QVBoxLayout(action_config_view)

        action_label = QLabel("Select an Action Type")
        action_layout.addWidget(action_label)

        actions = ["Click", "Move", "Nudge", "Swipe", "Type", "Wait", "Record position"]
        if len(self.actions) > 1:
            actions.append("Trigger macro")

        for action in actions:
            button = QPushButton(action)
            button.clicked.connect(lambda _, a=action: self.show_action_config_view(a.lower(), sender))
            action_layout.addWidget(button)

        if type(sender) is not AdvancedActions:
            back_button = QPushButton("Back")
            back_button.clicked.connect(self.switch_to_main_view)
            action_layout.addWidget(back_button)

        return action_config_view

    def show_action_config_view(self, action_type, sender):
        """
        Internal logic for switch_to_add_action_view, called after one of the choices for an action is pressed
        It switches to the requested action's UI in their Class, before returning to the prior def
        :param action_type: The option the user clicked on, that associates with an Action. These being click, wait,
            move, type and swipe
        :param sender: The app that wants to run this - send self (not needed if from MMM)
        """
        if type(sender) is not AdvancedActions:
            sender = self
        if action_type == "click":
            action_config_view = ClickXUI(sender)
        elif action_type == "wait":
            action_config_view = WaitUI(sender)
        elif action_type == "move":
            action_config_view = MouseToUI(sender)
        elif action_type == "nudge":
            action_config_view = NudgeMouseUI(sender)
        elif action_type == "type":
            action_config_view = TypeTextUI(sender)
        elif action_type == "swipe":
            action_config_view = SwipeXyUI(sender)
        elif action_type == "record position":
            action_config_view = RecordMousePositionUI(sender, self.actions[self.current_macro])
        elif action_type == "trigger macro":
            action_config_view = TriggerMacroUI(sender, self.macro_list)
        else:  # In case something weird gets called that isn't one of the above
            return

        self.central_widget.addWidget(action_config_view)
        self.central_widget.setCurrentWidget(action_config_view)

    def add_action(self, action):
        """
        This is called directly from the action Classes, and adds the action to self.actions. Updates the UI for the
        action list afterward
        :param action: The action (click, wait, move etc.) that was created by the interaction with the specific UI
            that was opened. They all implement the action ABC so are mutually compatible
        """
        self.actions[self.current_macro].append(action)
        self.update_action_list()

    def add_wait_between_all(self, wait):
        """
        A custom version of add_action for the Wait class. which adds a Wait between all non-wait actions.
        If it goes say type, wait, type, there will not be an additional wait added between the two types.
        No wait is added at index zero. These are intentionally all the same reference to Wait
        It updates the UI for actions after to show the added Waits
        :param wait: The created wait action to be added
        """
        if self.actions[self.current_macro]:
            for i in range(len(self.actions[self.current_macro]) - 1, 0, -1):
                if (not isinstance(self.actions[self.current_macro][i], Wait) and
                        not isinstance(self.actions[self.current_macro][i - 1], Wait)):
                    self.actions[self.current_macro].insert(i, wait)  # Use deepcopy instead to have unique Waits
            self.update_action_list()

    def switch_to_add_condition_view(self):
        """
        Called from pressing the + button on the conditions side
        This switches the UI to the ImageCondition Class for the user to make a condition, before returning to the
        main UI
        """
        self.central_widget.addWidget(self.image_config_view)
        self.central_widget.setCurrentWidget(self.image_config_view)

    def switch_to_main_view(self):
        """
        Returns to the main UI from wherever it was previously. If there's an event loop waiting for
        the UI to finish, this also quits it
        """
        self.central_widget.setCurrentWidget(self.main_view)

    def add_condition(self, condition, present_or_not):
        """
        Adds the new ImageCondition condition to either present or absent images, as specified by the user within
        the ImageCondition prompt. It then updates the condition list so that the user can see it
        :param condition: The ImageCondition object that the user made
        :param present_or_not: If the condition should go into the present_images or absent_images list
        """
        if present_or_not == "p":
            self.present_images[self.current_macro].append(condition)
        else:
            self.absent_images[self.current_macro].append(condition)
        self.update_condition_list()

    def update_action_list(self):
        """
        Refreshes the action list with all actions in actions so that all actions are visible to the user
        """
        self.action_list.clear()
        for action in self.actions[self.current_macro]:
            item = QListWidgetItem(str(action))
            item.setData(QtCore.Qt.ItemDataRole.UserRole, action)
            self.action_list.addItem(item)

    def update_condition_list(self):
        """
        Refreshes the condition list so that all conditions are visible to the user. They're detonated in the UI
        as "Present Image" or "Absent Image"
        """
        self.central_widget.cleanup_widgets()

        self.clear_condition_display(self.p_image_grid)
        self.clear_condition_display(self.a_image_grid)

        columns = int(self.p_grid_widget.width() // (self.image_dimensions * 17 / 15.7))

        for i in range(len(self.present_images[self.current_macro])):
            image, row, col = self.create_image(i, self.present_images, columns)
            self.p_image_grid.addWidget(image, row, col)

        for i in range(len(self.absent_images[self.current_macro])):
            label, row, col = self.create_image(i, self.absent_images, columns)
            self.a_image_grid.addWidget(label, row, col)

    @staticmethod
    def clear_condition_display(grid):
        """
        Clears and deletes all widgets from the passed in QGridLayout
        :param grid: The QGridLayout to clear
        """
        for i in reversed(range(grid.count())):
            item = grid.itemAt(i)
            widget = item.widget()
            grid.takeAt(i)
            widget.deleteLater()

    def create_image(self, i, image_list, columns):
        """
        Creates a ClickableLabel (a QLabel which can be right-clicked) based on the given image
        in the given image list which has the image inside of it, and returns said label, alongside
        the row and column that the label should be in
        :param i: The index of the image condition to get the pixmap from
        :param image_list: The image condition list
        :param columns: The number of columns of images there should be
        :return: A ClickableLabel with a QPixmap in it, and the row and col (ints) that the label should be in
        """
        pixmap = image_list[self.current_macro][i].image_pixmap
        label = ClickableLabel(self.right_click_condition_menu)
        label.setFixedSize(self.image_dimensions, self.image_dimensions)
        scaled_pixmap = pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row = i // columns
        col = i % columns
        return label, row, col

    def resizeEvent(self, event, **kwargs):
        self.update_condition_list()
        super().resizeEvent(event)

    def right_click_condition_menu(self, position, item):
        """
        The menu for right-clicking on an action or condition. It creates a clickable dropdown menu, that allows the
        user to delete the item
        :param position: The QPoint x, y coordinates that the user's mouse was at when the item was right-clicked on
        :param item: The item to be removed
        """
        menu = QMenu()
        remove_item = menu.addAction("Remove")
        selected_action = menu.exec(position)

        if selected_action == remove_item:
            self.remove_condition(item)

    def remove_condition(self, label):
        """
        Checks p_image_grid and a_image_grid for the item that matches the passed ClickableLabel, and removes it from
        the present / absent image list, alongside the grid
        :param label: The item to check. Must be a ClickableLabel to be matchable
        """
        for condition_list in (self.p_image_grid, self.a_image_grid):
            for i in range(condition_list.count()):
                if condition_list.itemAt(i).widget() == label:
                    if condition_list == self.p_image_grid:
                        self.present_images[self.current_macro].remove(self.present_images[self.current_macro][i])
                    else:
                        self.absent_images[self.current_macro].remove(self.absent_images[self.current_macro][i])
                    self.update_condition_list()
                    break

    def start_hotkey_listener(self):
        """
        Starts the thread for the listener for the hotkey
        """
        self.listener_thread = threading.Thread(target=self.run_listener, daemon=True)
        self.listener_thread.start()

    def start_action_thread(self):
        """Starts the thread that runs the macro"""
        self.macro_run_thread = threading.Thread(target=self.run_macro_thread, daemon=True)
        self.macro_run_thread.start()

    def run_listener(self):
        """Starts the listener, runs via the listener file. Passes in the on_hotkey_pressed definition"""
        listener.start_listener(self.on_hotkey_pressed)

    def run_macro_thread(self):
        """
        Thread for running the macro. Waits for a notification from on_hotkey_pressed, and runs it once notified, before
        resetting to idle
        """
        while True:
            with self.run_action_condition:
                self.run_action_condition.wait()

            while not self.macros_to_run.empty():
                # Says that the macro is running - if the previous one in the queue got cancelled early / to
                # substantiate it if new, then sets a class var (current_running_macro) to record which macro is running
                #  (to know when a hotkey is pressed if the macro should be added to the queue or not),
                #  and finally runs it
                self.running_macro = True
                self.current_running_macro = self.macros_to_run.get()
                if self.advanced_actions[self.current_running_macro]:
                    self.advanced_run_macro(self.current_running_macro)
                else:
                    self.run_macro(self.current_running_macro)

            self.run_button.setText("Run")
            [action.clear_coordinates() for i in range(len(self.actions)) for action in self.actions[i]
             if type(action) is RecordMousePosition]
            self.running_macro = False

    def on_hotkey_pressed(self, index):
        """
        Logic for when the hotkey is pressed. Triggers the macro thread when the macro isn't running, kills it
        when it is. It does this via notifying the macro thread
        :param index: The index of the macro to run
        """
        if not self.running_macro:
            if self.macros_to_run.empty():
                with self.mutex:
                    self.macros_to_run.put(index)
                with self.run_action_condition:
                    self.run_action_condition.notify()

        else:
            if self.current_running_macro != index:
                self.macros_to_run.put(index)
            else:
                self.run_button.setText("Stopping")
            self.running_macro = False
        if not self.listener_thread.is_alive():
            self.run_listener()

    def notify_action_thread(self, from_hotkey):
        """
        Notifies run_macro_thread to run, works via the hotkey or a press from the Run button. Also sets the
        run button to say Stop, which can be clicked to stop the macro (will display Stopping while stopping)
        """
        if not from_hotkey and self.run_button.text() == "Run":
            if self.macros_to_run.empty():
                with self.mutex:
                    self.macros_to_run.put(self.current_macro)
            self.run_button.setText("Stop")

        elif not from_hotkey and self.run_button.text() == "Stop":
            self.macros_to_run.empty()
            self.run_button.setText("Stopping")
            self.running_macro = False

        with self.run_action_condition:
            self.run_action_condition.notify()

    def get_macro_list(self):  # Maybe get rid of this in the future, it's used for one specific case
        return self.macro_list


def main():
    app = QApplication(sys.argv)

    with open('misc_utilities/main_style.qss', 'r') as file:
        dark_stylesheet = file.read()
    app.setStyleSheet(dark_stylesheet)

    main_window = MacroManagerMain()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
