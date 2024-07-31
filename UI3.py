import _pickle
import pickle
import sys
import threading
import inflect

from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QPoint, QEventLoop
from PyQt6.QtWidgets import *

from popups.HotkeyPopup import HotkeyPopup
from conditions.ImageCondition import *
from popups.RunCountPopup import RunCountPopup
from actions import *
from listener import *


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
        self.current_macro = 0

        self.start_hotkey_listener()  # Thread stuff - checking for the hotkey to run your script
        self.run_action_condition = threading.Condition()  # Notification for the thread that runs the macro
        self.start_action_thread()  # Thread that runs the macro
        self.running_macro = False  # Bool for if the macro is running or not
        self.run_count = 1  # The amount of times the script will run, associated with run_options

        self.hotkey = ["f8"]  # The default hotkey to start / stop the macro

        self.setWindowTitle("Macro Manager")
        self.setGeometry(400, 200, 1100, 700)

        self.central_widget = QStackedWidget()
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
        run_button = QPushButton("Run")
        run_button.setToolTip("Press " + str(self.hotkey) + " to kill the script")
        run_button.clicked.connect(self.notify_action_thread)

        self.run_options = QComboBox()
        self.run_options.addItem("Run once")
        self.run_options.addItem("Run infinitely")
        self.run_options.addItem("Custom run count")
        self.run_options.currentIndexChanged.connect(self.run_options_clicked)

        self.activation_key_button = QPushButton("Set a hotkey (currently " + str(self.hotkey[0]) + ")")
        self.activation_key_button.clicked.connect(self.hotkey_clicked)

        self.macro_list = QComboBox()
        self.macro_list.addItem("Macro one")
        self.macro_list.addItem("Create a new macro")
        self.macro_list.currentIndexChanged.connect(self.switch_macro)
        self.current_macro = 0  # Not strictly needed but writing self.macro_list.currentIndex() everywhere
        # is very clunky

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_actions)
        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_actions)
        top_layout.addWidget(run_button)
        top_layout.addWidget(self.run_options)
        top_layout.addWidget(self.activation_key_button)
        top_layout.addWidget(self.macro_list)
        top_layout.addWidget(save_button)
        top_layout.addWidget(load_button)
        self.main_layout.addLayout(top_layout)

    def init_action_condition_ui(self):
        """
        Initializes the main section of the UI where the actions and conditions are
        """
        middle_layout = QHBoxLayout()

        actions_frame = QFrame()  # Actions start here
        actions_frame.setFrameShape(QFrame.Shape.StyledPanel)
        actions_layout = QVBoxLayout(actions_frame)
        actions_label = QLabel("Actions")

        self.action_list = QListWidget()  # action_list has custom logic
        self.action_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # Right click
        self.action_list.customContextMenuRequested.connect(self.right_click_actions_menu)
        self.action_list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)  # Dragging
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

        conditions_frame = QFrame()  # Conditions start here
        conditions_frame.setFrameShape(QFrame.Shape.StyledPanel)
        conditions_layout = QVBoxLayout(conditions_frame)
        conditions_label = QLabel("Conditions")
        conditions_layout.addWidget(conditions_label)

        self.current_displayed_condition = None
        self.condition_list = QListWidget()
        self.condition_list.itemClicked.connect(self.display_selected_condition)
        self.condition_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # Right click menu
        self.condition_list.customContextMenuRequested.connect(self.right_click_actions_menu)
        conditions_layout.addWidget(self.condition_list)

        condition_button = QPushButton("+")
        condition_button.setFixedSize(40, 40)
        condition_button.setStyleSheet(plus_button_stylesheet)
        condition_button.clicked.connect(self.switch_to_add_condition_view)

        conditions_layout.addWidget(condition_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight |
                                                                QtCore.Qt.AlignmentFlag.AlignBottom)

        self.condition_display = QLabel()
        self.condition_display.setFixedSize(500, 270)
        self.condition_display.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        conditions_layout.addWidget(self.condition_display)

        middle_layout.addWidget(conditions_frame)

        self.main_layout.addLayout(middle_layout)
        self.central_widget.addWidget(self.main_view)
        self.central_widget.setCurrentWidget(self.main_view)

    def run_macro(self):
        """
        The main script to run the macro. It checks for if all the image conditions are present / absent, then runs
        the actions. Triggered from the run button or pressing the hotkey. Killed on pressing the hotkey as well
        Runs on action_thread, all internal definitions will also quit on hotkey press
        run_count being set to -1 means that it will run infinitely. Otherwise, the macro will run equal to the
        amount of times listed
        """
        if not self.actions:  # So processing power isn't wasted running a script that will trigger nothing
            return

        def check_images():
            """
            Checks if all the present images are present and absent ones are absent
            Stops if the hotkey is pressed
            """
            while self.running_macro:
                if all(image.run() for image in self.present_images[self.current_macro]) and all(
                        not image.run() for image in self.absent_images[self.current_macro]):
                    return

        def actions_run():
            """
            Runs the actions. All used actions will have a run() function
            Stops if the hotkey is pressed
            """
            for action in self.actions[self.current_macro]:
                if not self.running_macro:
                    return
                action.run()

        def run_loop():
            """
            The default loop to be used to check for images and then run the actions
            Stops if the hotkey is pressed
            """
            check_images()
            if self.running_macro:
                actions_run()

        if self.run_count > 0:
            for _ in range(self.run_count):
                if not self.running_macro:
                    break
                run_loop()

        elif self.run_count == - 1:
            while self.running_macro:
                run_loop()

    def start_hotkey_listener(self):
        """
        Starts the thread for the listener for the hotkey
        :return:
        """
        self.listener_thread = threading.Thread(target=self.run_listener, daemon=True)
        self.listener_thread.start()

    def start_action_thread(self):
        """Starts the thread that runs the macro"""
        self.macro_run_thread = threading.Thread(target=self.run_macro_thread, daemon=True)
        self.macro_run_thread.start()

    def run_listener(self):
        """Starts the listener, runs via Listener. Passes in the on_hotkey_pressed definition"""
        start_listener(self.on_hotkey_pressed)

    def on_hotkey_pressed(self):
        """
        Logic for when the hotkey is pressed. Triggers the macro thread when the macro isn't running, kills it
        when it is. It does this via notifying the macro thread
        """
        if not self.running_macro:
            self.notify_action_thread()
        else:
            self.running_macro = False
        if not self.listener_thread.is_alive():
            self.run_listener()

    def run_macro_thread(self):
        """
        Thread for running the macro. Waits for a notification from on_hotkey_pressed, and runs it once notified, before
        resetting to idle
        """
        while True:
            with self.run_action_condition:
                self.run_action_condition.wait()

            self.run_macro()

            self.running_macro = False

    def notify_action_thread(self):
        """
        Notifies run_macro_thread to run, works via the hotkey or a press from the Run button
        """
        self.running_macro = True
        with self.run_action_condition:
            self.run_action_condition.notify()

    def run_options_clicked(self, option):
        """
        Processes when the run count dropdown is clicked. If run once or infinite is clicked, sets run_count to 1 or -1
        When Run x times is clicked, opens run_count_popup, sets run_count to the number selected and creates a new
        option for it, or resets back to before if cancel is hit
        This only accepts positive integers
        :param option: The option that the user clicked on from the dropdown menu of run counts
        """
        if self.run_options.itemText(option) == "Run once":
            self.run_count = 1
        elif self.run_options.itemText(option) == "Run infinitely":
            self.run_count = -1

        elif self.run_options.itemText(option) == "Custom run count":
            self.run_options.blockSignals(True)  # The item selected changes during this def, retriggering
            popup = RunCountPopup(self)  # run_options_clicked so the signal needs to be blocked
            if popup.exec() == QDialog.DialogCode.Accepted:
                run_count = popup.runs
                if run_count == 1:  # If they say they want it to run once
                    self.run_options.setCurrentIndex(1)

                elif run_count > 1:
                    if self.run_options.count() < 4:
                        self.run_options.insertItem(1, "")
                    self.run_options.setItemText(1, "Run " + str(run_count) + " times")
                    self.run_options.setCurrentIndex(1)

                self.run_count = run_count

            else:
                if self.run_count == -1:  # If cancel is hit and they were on infinite
                    if self.run_options.count() == 4:  # Finds which index run infinite is at and sets run_options
                        self.run_options.setCurrentIndex(2)  # to it
                    else:
                        self.run_options.setCurrentIndex(1)
                elif self.run_count != 1:
                    self.run_options.setCurrentIndex(1)
                else:
                    self.run_options.setCurrentIndex(0)
            self.run_options.blockSignals(False)

    def switch_macro(self, option):
        """
        Allows the user to switch to a different action / create a new one
        :param option:
        """
        if self.macro_list.itemText(option) == "Create a new macro":
            self.macro_list.blockSignals(True)
            macro_position = len(self.macro_list) - 1
            self.macro_list.insertItem(macro_position, "Macro " +
                                       inflect.engine().number_to_words((macro_position + 1)))
            self.current_macro = macro_position
            self.macro_list.setCurrentIndex(macro_position)

            self.actions.append([])
            self.present_images.append([])
            self.absent_images.append([])
            self.macro_list.blockSignals(False)
        else:
            self.current_macro = self.macro_list.currentIndex()
        self.update_action_list()
        self.update_condition_list()

    def hotkey_clicked(self):
        """
        Logic for if the change start / stop button is clicked. Opens hotkey_popup and allows the user to set a new
        hotkey. The button is updated after with the new hotkey. If the user gives no input or an invalid input,
        the hotkey will be set to none
        """
        popup = HotkeyPopup(self.hotkey)
        if popup.exec() == QDialog.DialogCode.Accepted:
            try:
                self.hotkey = popup.key_combination
                self.activation_key_button.setText("Set a hotkey (currently " + str(self.hotkey[0]) + ")")
            except (IndexError, AttributeError):
                self.hotkey = []
                self.activation_key_button.setText("Set a hotkey (none set)")
            change_hotkey(self.hotkey)

    def startDrag(self, supportedActions):  # camelCase to match with PyQt5's def
        """
        Overwrites the startDrag def from PyQt5 to record the original row of the item that's being dragged and the item
        itself. Then calls the standard startDrag to drag the item. This is used for the actions list
        :param supportedActions: The default actions that are supported by PyQt5's start drag definition, here because
            supportedActions is a default parameter for the def
        :return:
        """
        self.action_list.start_pos = self.action_list.currentRow()
        self.action_list.dragged_item = self.action_list.currentItem()
        super(QListWidget, self.action_list).startDrag(supportedActions)

    def dropEvent(self, event):  # camelCase to match with PyQt5's def
        """
        Overwrites the dropEvent def from PyQt5. It still moves the UI element to the new position, but additionally
        moves the action object in self.action_list to the new position to permanently make the switch and have the
        macro run in the correct order
        :param event: The menu item that's dropped. A default parameter that comes with dropEvent from PyQt5
        """
        end_pos = self.action_list.indexAt(event.pos()).row()
        if self.action_list.dragged_item:
            action = self.actions[self.current_macro].pop(self.action_list.start_pos)
            self.actions[self.current_macro].insert(end_pos, action)
        super(QListWidget, self.action_list).dropEvent(event)
        self.update_action_list()

    def save_actions(self):
        """
        Saves the actions and conditions as a pickle file with a basic GUI file explorer dialogue
        """
        options = QFileDialog.Option(0)
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Macro", "",
                                                   "All Files (*);;Pickle Files (*.pkl)", options=options)
        if file_name:
            # The issue is that ImageConditions have a QPixmap inside of them. QPixmaps cannot be pickled, so
            # what's happening here is that all of them are being set to None so that they can be pickled,
            # and then recovered afterward
            for i in range(len(self.macro_list) - 1):
                [self.absent_images[i][j].clear_pixmap() for j in range(len(self.absent_images[i]))]
                [self.present_images[i][j].clear_pixmap() for j in range(len(self.present_images[i]))]

            with open(file_name, 'wb') as f:
                pickle.dump([self.actions, self.present_images, self.absent_images], f)

            for i in range(len(self.macro_list) - 1):
                [self.absent_images[i][j].recover_pixmap() for j in range(len(self.absent_images[i]))]
                [self.present_images[i][j].recover_pixmap() for j in range(len(self.present_images[i]))]

    def load_actions(self):
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

                if len(functions[0]) > 0:

                    base_length = len(self.actions) + 1
                    for i in range(len(functions[0])):
                        # Recovering the Condition QPixmaps (they're set to None, so they can be pickled)
                        [functions[1][i][j].recover_pixmap() for j in range(len(functions[1][i]))]
                        [functions[2][i][j].recover_pixmap() for j in range(len(functions[2][i]))]

                        self.macro_list.insertItem(len(self.actions), "Macro " +
                                                   inflect.engine().number_to_words(i + base_length))
                        self.actions.append(functions[0][i])
                        self.present_images.append(functions[1][i])
                        self.absent_images.append(functions[2][i])

                    self.macro_list.blockSignals(True)
                    self.current_macro = len(self.macro_list) - 2
                    self.macro_list.setCurrentIndex(len(self.macro_list) - 2)
                    self.macro_list.blockSignals(False)

                    self.condition_display.clear()
                    self.update_action_list()
                    self.update_condition_list()
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
        :return:
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
            self.action_config_view = SwipeXyUi(self)
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
                if not isinstance(self.actions[self.current_macro][i], Wait):
                    if not isinstance(self.actions[self.current_macro][i - 1], Wait):
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
        :return:
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
        self.condition_list.clear()
        for condition in self.present_images[self.current_macro]:
            item = QListWidgetItem("Present Image")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, condition)
            self.condition_list.addItem(item)
        for condition in self.absent_images[self.current_macro]:
            item = QListWidgetItem("Absent Image")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, condition)
            self.condition_list.addItem(item)

    def display_selected_condition(self, position):
        """
        For when the user clicks on one of the images in the condition list. It shows the image from the specified
        ImageCondition object in the bottom right of the UI
        :param position: The position in condition_list that was selected by the user. This specified the ImageCondition
            object to be displayed
        """

        condition = position.data(QtCore.Qt.ItemDataRole.UserRole)
        pixmap = condition.image_pixmap
        scaled_pixmap = pixmap.scaled(self.condition_display.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
        self.condition_display.setPixmap(scaled_pixmap)

        if condition in self.present_images[self.current_macro]:
            self.current_displayed_condition = self.present_images[self.current_macro].index(condition)
        elif condition in self.absent_images[self.current_macro]:
            self.current_displayed_condition = self.absent_images[self.current_macro].index(condition)

    def right_click_actions_menu(self, position: QPoint):
        """
        The menu for right-clicking on an action or condition. It creates a clickable dropdown menu, that allows the
        user to copy an item, edit one or delete the item. Copying and editing only work for actions. If the condition
        that's being displayed is deleted, it stops being displayed
        :param position: The x,y coordinates that the user's mouse was at when the right-clicked on the item
        """
        sender = self.sender()
        menu = QMenu()
        copy_item = None
        edit_item = None
        if sender is not self.condition_list:
            copy_item = menu.addAction("Copy")
            edit_item = menu.addAction("Edit")
        remove_item = menu.addAction("Remove")

        if sender == self.action_list or sender == self.condition_list:

            global_position = sender.viewport().mapToGlobal(position)  # Aligning the right click box
            selected_action = menu.exec(global_position)
            item = sender.itemAt(position)
            if item is not None:
                item = item.data(Qt.ItemDataRole.UserRole)

                if selected_action == remove_item:
                    if item in self.actions[self.current_macro]:
                        self.remove_action_or_condition(item, self.actions[self.current_macro])
                    elif item in self.absent_images[self.current_macro]:
                        if self.current_displayed_condition == self.absent_images[self.current_macro].index(item):
                            self.condition_display.clear()
                        self.remove_action_or_condition(item, self.absent_images[self.current_macro])
                    elif item in self.present_images[self.current_macro]:
                        if self.current_displayed_condition == self.present_images[self.current_macro].index(item):
                            self.condition_display.clear()
                        self.remove_action_or_condition(item, self.present_images[self.current_macro])

                elif selected_action == copy_item:
                    self.actions[self.current_macro].append(item)
                    self.update_action_list()

                elif selected_action == edit_item:
                    length_before_addition = len(self.actions[self.current_macro])
                    self.call_ui_with_params(item)
                    if len(self.actions[self.current_macro]) > length_before_addition:
                        item_index = self.actions[self.current_macro].index(item)
                        self.actions[self.current_macro][item_index] = self.actions[self.current_macro].pop()
                        self.update_action_list()

        sender.clearSelection()

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
            edit_view = SwipeXyUi(self, item)
        elif isinstance(item, TypeText):
            edit_view = TypeTextUI(self, item)
        elif isinstance(item, Wait):
            edit_view = WaitUI(self, item)
        else:
            return
        self.central_widget.addWidget(edit_view)
        self.central_widget.setCurrentWidget(edit_view)

        self.event_loop = QEventLoop()
        self.event_loop.exec()

    def remove_action_or_condition(self, item, item_list):
        """
        Removes the action / condition specified in right_click_actions_menu from their respective list, then
        updates the UI
        :param item: Either an Action or an ImageCondition (specified by the user)
        :param item_list: The associated list with the item. For Actions, this is actions, if it's a condition
            it'll either be present_images or absent_images
        """
        item_list.remove(item)
        if item_list is self.actions[self.current_macro]:
            self.update_action_list()
        else:
            self.update_condition_list()


def main():
    app = QApplication(sys.argv)

    with open('main_style.qss', 'r') as file:
        dark_stylesheet = file.read()

    app.setStyleSheet(dark_stylesheet)

    main_window = MacroManagerMain()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
