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
from pynput.keyboard import Key
import threading


class MacroManagerMain(QMainWindow):
    def __init__(self):
        super().__init__()

        self.actions = []
        self.present_images = []
        self.absent_images = []

        self.start_global_listener()  # Thread stuff - checking for the hotkey to run your script
        self.run_action_condition = threading.Condition()   # Notification for the thread that runs the macro
        self.start_action_thread()  # Thread that runs the macro

        self.setWindowTitle("Macro Manager")
        self.setGeometry(400, 200, 1100, 700)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()
        self.update_condition_list()

    def init_ui(self):
        self.main_view = QWidget()
        main_layout = QVBoxLayout(self.main_view)

        self.hotkey_pretty = "f8"  # Extra needed parameters. pretty is the one that's displayed to the user
        self.hotkey_useful = [Key.f8]   # The functional version of the hotkey. Not nice to look at though
        self.running_actions = False    # Bool for if the macro is running or not

        # Top buttons
        top_layout = QHBoxLayout()
        self.run_button = QPushButton("Run")
        self.run_button.setToolTip("Press " + str(self.hotkey_pretty) + " to kill the script")
        self.run_button.clicked.connect(self.notify_action_thread)

        self.run_options = QComboBox()
        self.run_options.addItem("Run once")
        self.run_options.addItem("Run infinitely")
        self.run_options.addItem("Run x times")
        self.run_options.currentIndexChanged.connect(self.run_options_clicked)

        self.run_count = 1  # The amount of times the script will run, associated with run_options

        self.activation_key_button = QPushButton("Click to change the start / stop hotkey")
        self.activation_key_button.clicked.connect(self.hotkey_clicked)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_actions)
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_actions)
        top_layout.addWidget(self.run_button)
        top_layout.addWidget(self.run_options)
        top_layout.addWidget(self.activation_key_button)
        top_layout.addWidget(self.save_button)
        top_layout.addWidget(self.load_button)
        main_layout.addLayout(top_layout)

        # Middle buttons
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
        self.action_list.startDrag = self.start_drag
        self.action_list.dropEvent = self.drop_event

        actions_layout.addWidget(actions_label)
        actions_layout.addWidget(self.action_list)

        self.add_action_button = QPushButton("+")
        self.add_action_button.setFixedSize(40, 40)
        self.add_action_button.setFont(QtGui.QFont("Arial", 20))
        self.add_action_button.setStyleSheet("border-radius: 20px; background-color: #007bff; color: white;")
        self.add_action_button.clicked.connect(self.switch_to_add_action_view)
        actions_layout.addWidget(self.add_action_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

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

        self.add_condition_button = QPushButton("+")
        self.add_condition_button.setFixedSize(40, 40)
        self.add_condition_button.setFont(QtGui.QFont("Arial", 20))
        self.add_condition_button.setStyleSheet("border-radius: 20px; background-color: #007bff; color: white;")
        self.add_condition_button.clicked.connect(self.switch_to_add_condition_view)

        conditions_layout.addWidget(self.add_condition_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 200)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        conditions_layout.addWidget(self.image_label)

        middle_layout.addWidget(conditions_frame)

        main_layout.addLayout(middle_layout)
        self.central_widget.addWidget(self.main_view)
        self.central_widget.setCurrentWidget(self.main_view)

    def run_actions(self):
        if not self.actions:  # So processing power isn't wasted running a script that will trigger nothing
            return

        def check_images():
            while self.running_actions:
                if not any(not image.run() for image in self.present_images) or any(
                        image.run() for image in self.absent_images):
                    return

        def actions_run():
            for action in self.actions:
                if not self.running_actions:
                    return
                action.run()

        def run_loop():
            check_images()
            if self.running_actions:
                actions_run()

        if self.run_count > 0:
            for _ in range(self.run_count):
                if not self.running_actions:
                    break
                run_loop()

        elif self.run_count == - 1:
            while self.running_actions:
                run_loop()

    def start_global_listener(self):
        self.listener_thread = threading.Thread(target=self.run_listener, daemon=True)
        self.listener_thread.start()

    def start_action_thread(self):
        self.action_thread = threading.Thread(target=self.run_action_thread, daemon=True)
        self.action_thread.start()

    def run_listener(self):
        start_listener(self.on_hotkey_pressed)

    def run_action_thread(self):
        while True:
            with self.run_action_condition:
                self.run_action_condition.wait()

            self.run_actions()

            self.running_actions = False

    def notify_action_thread(self):
        self.running_actions = True
        with self.run_action_condition:
            self.run_action_condition.notify()

    def on_hotkey_pressed(self):
        if not self.running_actions:
            self.notify_action_thread()
        else:
            self.running_actions = False
        if not self.listener_thread.is_alive():
            self.run_listener()

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
                    if self.run_options.count() == 4:
                        self.run_options.setCurrentIndex(2)
                    else:
                        self.run_options.setCurrentIndex(1)
                elif self.run_count != 1:
                    self.run_options.setCurrentIndex(1)
                else:
                    self.run_options.setCurrentIndex(0)
            self.run_options.blockSignals(False)

    def hotkey_clicked(self):
        popup = HotkeyPopup()
        print("into loop - hotkey popup")
        if popup.exec_() == QDialog.Accepted:
            print("dialogue accepted - hotkey popup")
            self.hotkey_useful = popup.key_combination
            self.hotkey_pretty = ", ".join(self.hotkey_useful)
            self.run_button.setToolTip("Or press " + str(self.hotkey_pretty) + " to start / stop the script")
            change_hotkey(self.hotkey_useful)

    def start_drag(self, supported_actions):
        self.action_list.start_pos = self.action_list.currentRow()
        self.action_list.dragged_item = self.action_list.currentItem()
        super(QListWidget, self.action_list).startDrag(supported_actions)

    def drop_event(self, event):
        end_pos = self.action_list.indexAt(event.pos()).row()
        if self.action_list.dragged_item:
            action = self.actions.pop(self.action_list.start_pos)
            self.actions.insert(end_pos, action)
        super(QListWidget, self.action_list).dropEvent(event)
        self.update_action_list()

    def save_actions(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Actions", "",
                                                   "All Files (*);;Pickle Files (*.pkl)", options=options)
        if file_name:
            print("Saving to " + file_name)
            with open(file_name, 'wb') as f:
                pickle.dump([self.actions, self.present_images, self.absent_images], f)

    def load_actions(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Actions", "",
                                                   "All Files (*);;Pickle Files (*.pkl)", options=options)
        try:
            if file_name:
                print("Loading from " + file_name)
                with open(file_name, 'rb') as f:
                    functions = pickle.load(f)
                self.actions.extend(functions[0])
                self.present_images.extend(functions[1])
                self.absent_images.extend(functions[2])
                self.update_action_list()
                self.update_condition_list()
        except _pickle.UnpicklingError:  # If you click on a non-pickle file
            pass

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

    def switch_to_add_condition_view(self):
        self.image_config_view = ImageConfigView(self)
        self.central_widget.addWidget(self.image_config_view)
        self.central_widget.setCurrentWidget(self.image_config_view)

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

    def switch_to_main_view(self):
        self.central_widget.setCurrentWidget(self.main_view)

    def add_action(self, action):
        self.actions.append(action)
        self.update_action_list()

    def add_wait_between_all(self, wait):
        if self.actions:
            for i in range(len(self.actions) - 1, -1, -1):
                if not isinstance(self.actions[i], Wait):
                    if not isinstance(self.actions[i - 1], Wait):
                        self.actions.insert(i, wait)
            self.update_action_list()

    def add_condition(self, condition, present_or_not):
        if present_or_not == "p":
            self.present_images.append(condition)
        else:
            self.absent_images.append(condition)
        self.update_condition_list()

    def update_action_list(self):
        self.action_list.clear()
        for action in self.actions:
            item = QListWidgetItem(str(action))
            item.setData(QtCore.Qt.UserRole, action)
            self.action_list.addItem(item)

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

    def display_selected_image(self, item):
        condition = item.data(QtCore.Qt.UserRole)
        pixmap = condition.get_image()
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), QtCore.Qt.KeepAspectRatio))

    def right_click_actions_menu(self, position: QPoint):
        sender = self.sender()
        menu = QMenu()
        remove_item = menu.addAction("Remove")

        if sender == self.action_list or sender == self.image_list:

            global_position = sender.viewport().mapToGlobal(position)  # Aligning the right click box
            selected_action = menu.exec_(global_position)

            if selected_action == remove_item:
                item = sender.itemAt(position)
                if item is not None:
                    item = item.data(Qt.UserRole)
                    if item in self.actions:
                        self.handle_remove_action(item, self.actions)
                    elif item in self.absent_images:
                        self.handle_remove_action(item, self.absent_images)
                    elif item in self.present_images:
                        self.handle_remove_action(item, self.present_images)

        sender.clearSelection()

    def handle_remove_action(self, item, item_list):
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
