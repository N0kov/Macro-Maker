import _pickle
import pickle
import sys
import threading
import inflect
import queue
import word2number.w2n as w2n

from PyQt6.QtCore import QEventLoop
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QAction

from conditions.ImageCondition import *
from popups.HotkeyPopup import HotkeyPopup
from popups.RemoveMacroPopup import RemoveMacroPopup
from popups.RenameMacroPopup import RenameMacroPopup
from popups.RunCountPopup import RunCountPopup
from actions import *
from misc_utilities import listener
from misc_utilities.ClickableQLabel import ClickableLabel


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
        self.hotkeys = ["f8"]
        self.run_counts = [1]
        listener.change_hotkey(self.hotkeys[0], 0)
        self.current_macro = 0
        self.macros_to_run = queue.Queue()
        self.mutex = threading.Lock()
        self.current_running_macro = -1

        self.start_hotkey_listener()  # Thread stuff - checking for the hotkey to run your script
        self.run_action_condition = threading.Condition()  # Notification for the thread that runs the macro
        self.start_action_thread()  # Thread that runs the macro
        self.running_macro = False  # Bool for if the macro is running or not

        self.setWindowTitle("Macro Manager")
        self.setGeometry(400, 200, 1100, 700)

        self.central_widget = QStackedWidget(self)
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

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.notify_action_thread)

        self.run_options = QComboBox()
        self.run_options.addItem("Run once")
        self.run_options.addItem("Run infinitely")
        self.run_options.addItem("Custom run count")
        self.run_options.currentIndexChanged.connect(self.run_options_clicked)

        self.set_hotkey_button = QPushButton("Set a hotkey (currently " + str(self.hotkeys[0]) + ")")
        self.set_hotkey_button.clicked.connect(self.hotkey_clicked)

        top_layout.addWidget(self.run_button)
        top_layout.addWidget(self.run_options)
        top_layout.addWidget(self.set_hotkey_button)
        top_layout.addWidget(self.macro_list)
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

        self.action_list = QListWidget(self)  # action_list has custom logic
        self.action_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # Right click
        self.action_list.customContextMenuRequested.connect(self.right_click_actions_menu)
        self.action_list.itemDoubleClicked.connect(self.edit_item)  # Double click = edit
        self.action_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)  # Dragging
        self.action_list.start_pos = None
        self.action_list.startDrag = self.startDrag
        self.action_list.dropEvent = self.dropEvent

        actions_layout.addWidget(actions_label)
        actions_layout.addWidget(self.action_list)

        plus_button_stylesheet = ("""
        QPushButton {
            border-radius: 20px;
            background-color: #007bff;
            color: white;
            font-family: Arial;
            font-size: 30px;
        }
        """)

        add_action_button = QPushButton("+")
        add_action_button.setFixedSize(40, 40)
        add_action_button.setStyleSheet(plus_button_stylesheet)
        add_action_button.clicked.connect(self.switch_to_add_action_view)
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

        condition_button = QPushButton("+")
        condition_button.setFixedSize(40, 40)
        condition_button.setStyleSheet(plus_button_stylesheet)
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
                # print(threading.active_count())

                self.run_loop(macro)

    def run_loop(self, macro):
        """
        The default loop to be used to check for images and then run the actions
        Stops if the hotkey is pressed
        :param macro: The index of the macro to run
        """
        self.check_images(macro)
        if self.running_macro:
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

    def switch_macro(self):  # macro_list could be set up to be a file dropdown menu style
        """
        Allows the user to switch to a different action / create one / remove a macro. Macros are only removable when
        there are at least two present
        """
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
            self.present_images.pop(removal_index)
            self.absent_images.pop(removal_index)
            listener.remove_hotkey(removal_index)

            self.fix_macro_list_names()
            for i in range(len(self.actions)):
                for j in range(len(self.actions[i])):
                    if TriggerMacro is type(self.actions[i][j]):
                        print("Removal index: " + str(removal_index))
                        print("Macro index: " + str(self.actions[i][j].get_index()))
                        if removal_index == self.actions[i][j].get_index():
                            self.actions[i].pop(j)
                        elif removal_index < self.actions[i][j].get_index():
                            self.actions[i][j].update_fields((-1), self.macro_list.itemText(removal_index - 1))

            self.macro_list.blockSignals(False)
            self.macro_list.setCurrentIndex(0)  # This is effectively recalling this method and going to else
        else:
            self.macro_list.setCurrentIndex(0)  # Same here

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

        if self.macro_list.count() == 4:
            self.macro_list.removeItem(3)
        else:
            if self.macro_list.itemText(self.macro_list.count() - 1) != "Remove a macro":
                self.macro_list.addItem("Remove a macro")

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

    def startDrag(self, supportedActions):  # camelCase to match with PyQt5's def
        """
        Overwrites the startDrag def from PyQt5 to record the original row of the item that's being dragged and the item
        itself. Then calls the standard startDrag to drag the item. This is used for the actions list
        :param supportedActions: The default actions that are supported by PyQt5's start drag definition, here because
            supportedActions is a default parameter for the def
        """
        self.action_list.start_pos = self.action_list.currentRow()
        self.action_list.dragged_item = self.action_list.currentItem()
        super(QListWidget, self.action_list).startDrag(supportedActions)

    def dropEvent(self, event, **kwargs):  # camelCase to match with PyQt5's def
        """
        Overwrites the dropEvent def from PyQt5. It still moves the UI element to the new position, but additionally
        moves the action object in self.action_list to the new position to permanently make the switch and have the
        macro run in the correct order
        :param event: The menu item that's dropped. A default parameter that comes with dropEvent from PyQt5
        """
        end_pos = self.action_list.indexAt(event.position().toPoint()).row()

        if end_pos == -1:
            end_pos = self.action_list.count()
        elif event.position().toPoint().y() < self.action_list.visualItemRect(self.action_list.item(0)).top():
            end_pos = 0

        if self.action_list.dragged_item:
            action = self.actions[self.current_macro].pop(self.action_list.start_pos)
            self.actions[self.current_macro].insert(end_pos, action)
        super(QListWidget, self.action_list).dropEvent(event)
        self.update_action_list()

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
                             self.hotkeys, self.run_counts, macro_name_list], f)

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

                    if functions[3][i] not in self.hotkeys:
                        self.hotkeys.append(functions[3][i])
                    else:
                        self.hotkeys.append("")
                    listener.change_hotkey(self.hotkeys[-1], (len(self.macro_list)))

                self.current_macro = len(self.actions) - 1
                self.macro_list.setCurrentIndex(self.current_macro)
                self.fix_macro_list_names()

                for i in range(base_length, len(self.actions)):  # The names need to be fixed before this can run
                    [action.update_fields(base_length, self.macro_list.itemText(i))
                     for action in self.actions[i] if isinstance(action, TriggerMacro)]

                if self.hotkeys[self.current_macro] != "":
                    self.set_hotkey_button.setText("Set a hotkey (currently " +
                                                   str(self.hotkeys[self.current_macro]) + ")")
                else:
                    self.set_hotkey_button.setText("Set a hotkey")

                self.set_run_options_from_run_counts()
                self.update_condition_list()
                self.update_action_list()

                self.macro_list.blockSignals(False)

        except (_pickle.UnpicklingError, EOFError):  # If you click on a non-pickle file / a corrupt pkl file
            pass

    def switch_to_add_action_view(self):
        """
        Called from the + button in the actions side
        The base UI for picking a new action to be made. Allows the user to pick an action from a list, and then
        opens the screen for said action. Also includes a back button if they decide to not add an action
        """
        self.action_config_view = QWidget()
        action_layout = QVBoxLayout(self.action_config_view)

        action_label = QLabel("Select an Action Type")
        action_layout.addWidget(action_label)

        actions = ["Click", "Move", "Swipe", "Type", "Wait"]
        if len(self.actions) > 1:
            actions.append("Trigger macro")

        for action in actions:
            button = QPushButton(action)
            button.clicked.connect(lambda _, a=action: self.show_action_config_view(a.lower()))
            action_layout.addWidget(button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.switch_to_main_view)
        action_layout.addWidget(back_button)

        self.central_widget.addWidget(self.action_config_view)
        self.central_widget.setCurrentWidget(self.action_config_view)

    def show_action_config_view(self, action_type):
        """
        Internal logic for switch_to_add_action_view, called after one of the choices for an action is pressed
        It switches to the requested action's UI in their Class, before returning to the prior def
        :param action_type: The option the user clicked on, that associates with an Action. These being click, wait,
            move, type and swipe
        """
        if action_type == "click":
            self.action_config_view = ClickXUI(self)
        elif action_type == "wait":
            self.action_config_view = WaitUI(self)
        elif action_type == "move":
            self.action_config_view = MouseToUI(self)
        elif action_type == "type":
            self.action_config_view = TypeTextUI(self)
        elif action_type == "swipe":
            self.action_config_view = SwipeXyUI(self)
        elif action_type == "trigger macro":
            self.action_config_view = TriggerMacroUI(self, self.macro_list)
        else:  # In case something weird gets called that isn't one of the above
            return

        self.central_widget.addWidget(self.action_config_view)
        self.central_widget.setCurrentWidget(self.action_config_view)

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
        No wait is added at index zero
        It updates the UI for actions after to show the added Waits
        :param wait: The created wait action to be added
        """
        if self.actions[self.current_macro]:
            for i in range(len(self.actions[self.current_macro]) - 1, 0, -1):
                if (not isinstance(self.actions[self.current_macro][i], Wait) and
                        not isinstance(self.actions[self.current_macro][i - 1], Wait)):
                    self.actions[self.current_macro].insert(i, wait)
            self.update_action_list()

    def switch_to_add_condition_view(self):
        """
        Called from pressing the + button on the conditions side
        This switches the UI to the ImageCondition Class for the user to make a condition, before returning to the
        main UI
        """
        self.image_config_view = ImageConditionUI(self)
        self.central_widget.addWidget(self.image_config_view)
        self.central_widget.setCurrentWidget(self.image_config_view)

    def switch_to_main_view(self):
        """
        Returns to the main UI from wherever it was previously. If there's an event loop waiting for
        the UI to finish, this also quits it
        """
        self.central_widget.setCurrentWidget(self.main_view)
        if hasattr(self, 'event_loop') and self.event_loop.isRunning():
            self.event_loop.quit()

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
        self.clear_condition_display(self.p_image_grid)
        self.clear_condition_display(self.a_image_grid)

        columns = int(self.p_grid_widget.width() // (self.image_dimensions * 17/15.7))

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

    def right_click_actions_menu(self, position):
        """
        The menu for right-clicking on an action or condition. It creates a clickable dropdown menu, that allows the
        user to copy an item, edit one or delete the item.
        :param position: The QPoint x,y coordinates that the user's mouse was at when the right-clicked on the item
        """
        sender = self.sender()
        menu = QMenu()
        copy_item = menu.addAction("Copy")
        edit_item = menu.addAction("Edit")
        remove_item = menu.addAction("Remove")

        if sender == self.action_list:

            global_position = sender.viewport().mapToGlobal(position)
            selected_action = menu.exec(global_position)
            item = sender.itemAt(position)
            if item is not None:
                item = item.data(Qt.ItemDataRole.UserRole)

                if selected_action == remove_item:
                    if item in self.actions[self.current_macro]:  # Should always be True, but being safe
                        self.actions[self.current_macro].remove(item)
                        self.update_action_list()

                elif selected_action == copy_item:
                    self.actions[self.current_macro].append(item)
                    self.update_action_list()

                elif selected_action == edit_item:
                    self.edit_item(item)

        sender.clearSelection()

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

    def edit_item(self, item):
        """
        Opens the item's UI, and alters the chosen item to match what the user edited it to be
        :param item: The item to be edited. Can be an Action, or a QListWidgetItem
        """
        if QListWidgetItem is type(item):
            item = item.data(Qt.ItemDataRole.UserRole)

        length_before_edit = len(self.actions[self.current_macro])
        self.call_ui_with_params(item)
        if len(self.actions[self.current_macro]) > length_before_edit:
            item_index = self.actions[self.current_macro].index(item)
            self.actions[self.current_macro][item_index] = self.actions[self.current_macro].pop()
            self.update_action_list()

    def call_ui_with_params(self, item):
        """
        Calls the UI for the specified item, with the current item's data passed in so the user can edit it
        This waits until the UI is closed to allow the script to close
        :param item: The action to be edited
        """
        if isinstance(item, ClickX):
            edit_view = ClickXUI(self, item)
        elif isinstance(item, MouseTo):
            edit_view = MouseToUI(self, item)
        elif isinstance(item, SwipeXY):
            edit_view = SwipeXyUI(self, item)
        elif isinstance(item, TypeText):
            edit_view = TypeTextUI(self, item)
        elif isinstance(item, Wait):
            edit_view = WaitUI(self, item)
        elif isinstance(item, TriggerMacro):
            edit_view = TriggerMacroUI(self, self.macro_list, item)
        else:
            return
        self.central_widget.addWidget(edit_view)
        self.central_widget.setCurrentWidget(edit_view)

        self.event_loop = QEventLoop()
        self.event_loop.exec()

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
                print(threading.active_count())
                self.running_macro = True
                self.current_running_macro = self.macros_to_run.get()
                self.run_macro(self.current_running_macro)

            self.run_button.setText("Run")
            print()
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
                    # self.macros_to_run.put(self.current_macro)
                    self.macros_to_run.put(index)
                # self.notify_action_thread(True)
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
