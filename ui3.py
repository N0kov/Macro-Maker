import sys
import pickle
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from actions import Wait
from Listener import start_listener, continue_script
from ImageConditions import ImageConfigView
from actions import ClickXUI, WaitUI, MouseToUI, TypeTextUI, SwipeXyUi
from PyQt5.QtCore import Qt, QPoint

class MacroManagerMain(QMainWindow):
    def __init__(self):
        super().__init__()

        self.actions = []
        self.present_images = []
        self.absent_images = []

        self.setWindowTitle("Macro Manager")
        self.setGeometry(400, 200, 1100, 700)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()
        self.update_condition_list()

    def init_ui(self):
        self.main_view = QWidget()
        main_layout = QVBoxLayout(self.main_view)

        # Menu buttons at the top
        top_layout = QHBoxLayout()
        self.run_button = QPushButton("Run options (press shift to kill the script)")
        self.run_button.clicked.connect(self.run_actions)

        self.run_combo = QComboBox()
        self.run_combo.addItem("Run once")
        self.run_combo.addItem("Run infinitely")

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_actions)
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_actions)
        top_layout.addWidget(self.run_button)
        top_layout.addWidget(self.run_combo)
        top_layout.addWidget(self.save_button)
        top_layout.addWidget(self.load_button)
        main_layout.addLayout(top_layout)

        # Actions and conditions
        middle_layout = QHBoxLayout()

        # Actions
        actions_frame = QFrame()
        actions_frame.setFrameShape(QFrame.StyledPanel)
        actions_layout = QVBoxLayout(actions_frame)
        actions_label = QLabel("Actions")
        self.action_list = QListWidget()
        self.action_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.action_list.customContextMenuRequested.connect(self.right_click_menu)
        actions_layout.addWidget(actions_label)
        actions_layout.addWidget(self.action_list)

        self.add_action_button = QPushButton("+")
        self.add_action_button.setFixedSize(40, 40)
        self.add_action_button.setFont(QtGui.QFont("Arial", 20))
        self.add_action_button.setStyleSheet("border-radius: 20px; background-color: #007bff; color: white;")
        self.add_action_button.clicked.connect(self.switch_to_add_action_view)
        actions_layout.addWidget(self.add_action_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        middle_layout.addWidget(actions_frame)

        # Conditions Section
        conditions_frame = QFrame()
        conditions_frame.setFrameShape(QFrame.StyledPanel)
        conditions_layout = QVBoxLayout(conditions_frame)
        conditions_label = QLabel("Conditions")
        conditions_layout.addWidget(conditions_label)

        self.image_list = QListWidget()
        self.image_list.itemClicked.connect(self.display_selected_image)
        self.image_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_list.customContextMenuRequested.connect(self.right_click_menu)
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

        run_infinite = False
        if self.run_combo.currentText() == "Run infinitely":
            run_infinite = True

        start_listener()
        print("running, infinite = " + str(run_infinite))

        while True:
            while continue_script():
                if not any(not image.run() for image in self.present_images) or any(
                        image.run() for image in self.absent_images):
                    break
            for action in self.actions:
                if not continue_script():
                    return
                action.run()
            if not run_infinite:  # This was causing issues when I had this if statement and the if below on one line
                return
            if not continue_script():
                return

    def save_actions(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Actions", "",
                                                   "All Files (*);;Pickle Files (*.pkl)", options=options)
        if file_name:
            print(f"Saving actions to {file_name}...")
            with open(file_name, 'wb') as f:
                pickle.dump([self.actions, self.present_images, self.absent_images], f)

    def load_actions(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Actions", "",
                                                   "All Files (*);;Pickle Files (*.pkl)", options=options)
        if file_name:
            print(f"Loading actions from {file_name}...")
            with open(file_name, 'rb') as f:
                functions = pickle.load(f)
            self.actions.extend(functions[0])
            self.present_images.extend(functions[1])
            self.absent_images.extend(functions[2])
            self.update_action_list()
            self.update_condition_list()

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
            for i in range(len(self.actions) - 1, 0, -1):
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

    def right_click_menu(self, position: QPoint):
        # Options
        sender = self.sender()
        menu = QMenu()
        remove_item = menu.addAction("Remove")

        if sender == self.action_list or sender == self.image_list:

            # Aligning the right click box
            global_position = sender.viewport().mapToGlobal(position)
            selected_action = menu.exec_(global_position)

            # Remove clicked
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
