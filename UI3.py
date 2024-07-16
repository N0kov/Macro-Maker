import sys
import pickle
import _pickle
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from Listener import *
from ImageConditions import ImageConfigView
from actions import ClickXUI, WaitUI, MouseToUI, TypeTextUI, SwipeXyUi, Wait
from PyQt5.QtCore import Qt, QPoint
from run_count_popup import RunCountPopup
from hotkey_popup import HotkeyPopup
import threading


class MacroManagerMain(QMainWindow):
    def __init__(self):
        super().__init__()

        self.actions = []
        self.present_images = []
        self.absent_images = []

        self.start_hotkey_listener()  # Thread stuff - checking for the hotkey to run your script
        self.run_action_condition = threading.Condition()   # Notification for the thread that runs the macro
        self.start_action_thread()  # Thread that runs the macro
        self.running_macro = False  # Bool for if the macro is running or not
        self.run_count = 1  # The amount of times the script will run, associated with run_options

        self.hotkey = "f8"  # The default hotkey to start / stop the macro

        self.setWindowTitle("Macro Manager")
        self.setGeometry(400, 200, 1100, 700)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.main_view = QWidget()
        self.main_layout = QVBoxLayout(self.main_view)

        self.init_top_ui()
        self.init_action_condition_ui()
        self.update_condition_list()

    # Initializes the top section of the UI where the buttons are for running, changing the run count, etc.
    def init_top_ui(self):
        top_layout = QHBoxLayout()
        run_button = QPushButton("Run")
        run_button.setToolTip("Press " + str(self.hotkey) + " to kill the script")
        run_button.clicked.connect(self.notify_action_thread)

        self.run_options = QComboBox()
        self.run_options.addItem("Run once")
        self.run_options.addItem("Run infinitely")
        self.run_options.addItem("Run x times")
        self.run_options.currentIndexChanged.connect(self.run_options_clicked)

        self.activation_key_button = QPushButton("Set a hotkey (currently " + self.hotkey + ")")
        self.activation_key_button.clicked.connect(self.hotkey_clicked)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_actions)
        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_actions)
        top_layout.addWidget(run_button)
        top_layout.addWidget(self.run_options)
        top_layout.addWidget(self.activation_key_button)
        top_layout.addWidget(save_button)
        top_layout.addWidget(load_button)
        self.main_layout.addLayout(top_layout)

    # Initializes the main section of the UI where the actions and conditions are
    def init_action_condition_ui(self):
        middle_layout = QHBoxLayout()

        actions_frame = QFrame()  # Actions start here
        actions_frame.setFrameShape(QFrame.StyledPanel)
        actions_layout = QVBoxLayout(actions_frame)
        actions_label = QLabel("Actions")

        self.action_list = QListWidget()   # action_list has custom logic
        self.action_list.setContextMenuPolicy(Qt.CustomContextMenu)  # Right click
        self.action_list.customContextMenuRequested.connect(self.right_click_actions_menu)
        self.action_list.setDragDropMode(QAbstractItemView.DragDrop)  # Dragging
        self.action_list.start_pos = None
        self.action_list.startDrag = self.startDrag
        self.action_list.dropEvent = self.dropEvent

        actions_layout.addWidget(actions_label)
        actions_layout.addWidget(self.action_list)

        add_action_button = QPushButton("+")
        add_action_button.setFixedSize(40, 40)
        add_action_button.setFont(QtGui.QFont("Arial", 20))
        add_action_button.setStyleSheet("border-radius: 20px; background-color: #007bff; color: white;")
        add_action_button.clicked.connect(self.switch_to_add_action_view)
        actions_layout.addWidget(add_action_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        middle_layout.addWidget(actions_frame)

        conditions_frame = QFrame()  # Conditions start here
        conditions_frame.setFrameShape(QFrame.StyledPanel)
        conditions_layout = QVBoxLayout(conditions_frame)
        conditions_label = QLabel("Conditions")
        conditions_layout.addWidget(conditions_label)

        self.image_list = QListWidget()
        self.image_list.itemClicked.connect(self.display_selected_image)
        self.image_list.setContextMenuPolicy(Qt.CustomContextMenu)  # Right click menu
        self.image_list.customContextMenuRequested.connect(self.right_click_actions_menu)
        conditions_layout.addWidget(self.image_list)

        condition_button = QPushButton("+")
        condition_button.setFixedSize(40, 40)
        condition_button.setFont(QtGui.QFont("Arial", 20))
        condition_button.setStyleSheet("border-radius: 20px; background-color: #007bff; color: white;")
        condition_button.clicked.connect(self.switch_to_add_condition_view)

        conditions_layout.addWidget(condition_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 200)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        conditions_layout.addWidget(self.image_label)

        middle_layout.addWidget(conditions_frame)

        self.main_layout.addLayout(middle_layout)
        self.central_widget.addWidget(self.main_view)
        self.central_widget.setCurrentWidget(self.main_view)

    # The main script to run the macro. It checks for if all the image conditions are present / absent, then runs
    # the actions. Triggered from the run button or pressing the hotkey. Killed on pressing the hotkey as well
    # Runs on action_thread, all internal definitions will also quit on hotkey press
    def run_macro(self):
        if not self.actions:  # So processing power isn't wasted running a script that will trigger nothing
            return

        # Checks if all the present images are present and absent ones are absent
        def check_images():
            while self.running_macro:
                if not any(not image.run() for image in self.present_images) or any(
                        image.run() for image in self.absent_images):
                    return

        # Runs the actions. All used actions will have a run() function
        def actions_run():
            for action in self.actions:
                if not self.running_macro:
                    return
                action.run()

        # The default loop to be used to check for images and then run the actions
        def run_loop():
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

    # Starts the thread for the listener for the hotkey
    def start_hotkey_listener(self):
        self.listener_thread = threading.Thread(target=self.run_listener, daemon=True)
        self.listener_thread.start()

    # Starts the thread that runs the macro
    def start_action_thread(self):
        self.macro_run_thread = threading.Thread(target=self.run_macro_thread, daemon=True)
        self.macro_run_thread.start()

    # Starts the listener, runs via Listener. Passes in the on_hotkey_pressed definition
    def run_listener(self):
        start_listener(self.on_hotkey_pressed)

    # Logic for when the hotkey is pressed. Triggers the macro thread when the macro isn't running, kills it
    # when it is. It does this via notifying the macro thread
    def on_hotkey_pressed(self):
        if not self.running_macro:
            self.notify_action_thread()
        else:
            self.running_macro = False
        if not self.listener_thread.is_alive():
            self.run_listener()

    # Thread for running the macro. Waits for a notification from on_hotkey_pressed, and runs it once notified, before
    # resetting to idle
    def run_macro_thread(self):
        while True:
            with self.run_action_condition:
                self.run_action_condition.wait()

            self.run_macro()

            self.running_macro = False

    # Notifies run_macro_thread to run, works via the hotkey or a press from the Run button
    def notify_action_thread(self):
        self.running_macro = True
        with self.run_action_condition:
            self.run_action_condition.notify()

    # Processes when the run count dropdown is clicked. If run once or infinite is clicked, sets run_count to 1 or -1
    # When Run x times is clicked, opens run_count_popup, sets run_count to the number selected and creates a new
    # option for it, or resets back to before if cancel is hit
    # This only accepts positive integers
    def run_options_clicked(self, option):
        if self.run_options.itemText(option) == "Run once":
            self.run_count = 1
        elif self.run_options.itemText(option) == "Run infinitely":
            self.run_count = -1

        elif self.run_options.itemText(option) == "Run x times":
            self.run_options.blockSignals(True)  # The item selected changes during this def, retriggering
            popup = RunCountPopup(self)  # run_options_clicked so the signal needs to be blocked
            if popup.exec_() == QDialog.Accepted:
                run_count = popup.runs
                if run_count == 1:  # If they say they want it to run once
                    self.run_options.setCurrentIndex(1)

                elif run_count > 1:
                    if self.run_options.count() < 4:
                        self.run_options.insertItem(1, "")
                    self.run_options.setItemText(2, "Run " + str(run_count) + " times")
                    self.run_options.setCurrentIndex(2)
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

    # Logic for if the change start / stop button is clicked. Opens hotkey_popup and allows the user to set a new
    # hotkey. The button is updated after with the new hotkey
    def hotkey_clicked(self):
        popup = HotkeyPopup()
        if popup.exec_() == QDialog.Accepted:
            self.hotkey = popup.key_combination
            try:
                self.activation_key_button.setText("Set a hotkey (currently " + str(self.hotkey[0]) + ")")
                change_hotkey(self.hotkey)
            except IndexError:
                pass

    # Overwrites the startDrag def from PyQt5 to record the original row of the item that's being dragged and the item
    # itself. Then calls the standard startDrag to drag the item. This is used for the actions list
    def startDrag(self, supported_actions):  # camelCase to match with PyQt5's def
        self.action_list.start_pos = self.action_list.currentRow()
        self.action_list.dragged_item = self.action_list.currentItem()
        super(QListWidget, self.action_list).startDrag(supported_actions)

    # Overwrites the dropEvent def from PyQt5. It still moves the UI element to the new position, but additionally
    # moves the action object in self.action_list to the new position to permanently make the switch and have the
    # macro run in the correct order
    def dropEvent(self, event):  # camelCase to match with PyQt5's def
        end_pos = self.action_list.indexAt(event.pos()).row()
        if self.action_list.dragged_item:
            action = self.actions.pop(self.action_list.start_pos)
            self.actions.insert(end_pos, action)
        super(QListWidget, self.action_list).dropEvent(event)
        self.update_action_list()

    # Saves the actions and conditions as a pickle file with a basic GUI file explorer dialogue
    def save_actions(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Actions", "",
                                                   "All Files (*);;Pickle Files (*.pkl)", options=options)
        if file_name:
            # print("Saving to " + file_name)
            with open(file_name, 'wb') as f:
                pickle.dump([self.actions, self.present_images, self.absent_images], f)

    # Loads the actions and conditions from a specified file in a GUI dialogue. This must be a pickle file, if
    # not it will just pass. This extends the preexisting actions, present_images and absent_images lists, so
    # any actions and / or conditions that are already be present will stay at the front
    def load_actions(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Actions", "",
                                                   "All Files (*);;Pickle Files (*.pkl)", options=options)
        try:
            if file_name:
                # print("Loading from " + file_name)
                with open(file_name, 'rb') as f:
                    functions = pickle.load(f)
                self.actions.extend(functions[0])
                self.present_images.extend(functions[1])
                self.absent_images.extend(functions[2])
                self.update_action_list()
                self.update_condition_list()
        except _pickle.UnpicklingError:  # If you click on a non-pickle file
            pass

    # Called from the + button in the actions side
    # The base UI for picking a new action to be made. Allows the user to pick an action from a list, and then
    # opens the screen for said action. Also includes a back button if they decide to not add an action
    def switch_to_add_action_view(self):
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

    # Internal logic for switch_to_add_action_view, called after one of the choices for an action is pressed
    # It switches to the requested action's UI in their Class, before returning to the prior def
    def show_action_config_view(self, action_type):
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
        else:     # In case something weird gets called that isn't one of the above
            return

        self.central_widget.addWidget(self.action_config_view)
        self.central_widget.setCurrentWidget(self.action_config_view)

    # This is called directly from the action Classes, and adds the action to self.actions. Updates the UI for the
    # action list afterward
    def add_action(self, action):
        self.actions.append(action)
        self.update_action_list()

    # A custom version of add_action for the Wait class. If the user asks to have a delay between all non-wait actions,
    # this does that. If it goes say type, wait, type, there will not be an additional wait added between the two types
    # It updates the UI for actions after to show the Waits
    def add_wait_between_all(self, wait):
        if self.actions:
            for i in range(len(self.actions) - 1, 0, -1):
                if not isinstance(self.actions[i], Wait):
                    if not isinstance(self.actions[i - 1], Wait):
                        self.actions.insert(i, wait)
            self.update_action_list()

    # Called from pressing the + button on the conditions side
    # This switches the UI to the ImageConditions Class for the user to make a condition, before returning to the
    # main UI
    def switch_to_add_condition_view(self):
        self.image_config_view = ImageConfigView(self)
        self.central_widget.addWidget(self.image_config_view)
        self.central_widget.setCurrentWidget(self.image_config_view)

    # Returns to the main UI from wherever it was previously
    def switch_to_main_view(self):
        self.central_widget.setCurrentWidget(self.main_view)

    # Adds the new ImageConditions condition to either present or absent images, as specified by the user within
    # the ImageConditions prompt. It then updates the condition list so that the user can see it
    def add_condition(self, condition, present_or_not):
        if present_or_not == "p":
            self.present_images.append(condition)
        else:
            self.absent_images.append(condition)
        self.update_condition_list()

    # Refreshes the action list with all actions in self.actions so that all actions are visible to the user
    def update_action_list(self):
        self.action_list.clear()
        for action in self.actions:
            item = QListWidgetItem(str(action))
            item.setData(QtCore.Qt.UserRole, action)
            self.action_list.addItem(item)

    # Refreshes the condition list so that all conditions are visible to the user. They're detonated in the UI
    # as "Present Image" or "Absent Image"
    def update_condition_list(self):
        self.image_list.clear()
        for condition in self.present_images:
            item = QListWidgetItem("Present Image")
            item.setData(QtCore.Qt.UserRole, condition)
            self.image_list.addItem(item)
        for condition in self.absent_images:
            item = QListWidgetItem("Absent Image")
            item.setData(QtCore.Qt.UserRole, condition)
            self.image_list.addItem(item)

    # For when the user clicks on one of the images in the condition list. It shows the image from the specified
    # ImageConditions in the bottom right
    def display_selected_image(self, item):
        condition = item.data(QtCore.Qt.UserRole)
        pixmap = condition.get_image()
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), QtCore.Qt.KeepAspectRatio))

    # The menu for right-clicking on an action or condition. It creates an interface next to the mouse
    # to with a delete box which when clicked on will delete the selected action or condition from the list
    def right_click_actions_menu(self, position: QPoint):
        sender = self.sender()
        menu = QMenu()
        remove_item = menu.addAction("Remove")  # There may be an edit action or edit condition option added
                                                # in the future
        if sender == self.action_list or sender == self.image_list:

            global_position = sender.viewport().mapToGlobal(position)  # Aligning the right click box
            selected_action = menu.exec_(global_position)

            if selected_action == remove_item:
                item = sender.itemAt(position)
                if item is not None:
                    item = item.data(Qt.UserRole)
                    if item in self.actions:
                        self.remove_action_or_condition(item, self.actions)
                    elif item in self.absent_images:
                        self.remove_action_or_condition(item, self.absent_images)
                    elif item in self.present_images:
                        self.remove_action_or_condition(item, self.present_images)

        sender.clearSelection()

    # Removes the action / condition specified in right_click_actions_menu from their respective list, then
    # updates the UI
    def remove_action_or_condition(self, item, item_list):
        item_list.remove(item)
        if item_list is self.actions:
            self.update_action_list()
        else:
            self.update_condition_list()


def main():
    app = QApplication(sys.argv)
    main_window = MacroManagerMain()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
