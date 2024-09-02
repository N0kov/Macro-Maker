from PyQt6.QtWidgets import (QSizePolicy, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit,
                             QListWidget, QHBoxLayout, QListWidgetItem, QWidget)
from PyQt6 import QtCore, QtWidgets

from misc_utilities.CustomDraggableList import CustomDraggableList


class AdvancedActions(QtWidgets.QWidget):
    def __init__(self, main_app, current_setup):
        super(AdvancedActions, self).__init__()
        self.main_app = main_app

        self.actions = []
        self.current_macro = 0  # Purely here for compatibility with CustomDraggableList

        self.macro_list = self.main_app.macro_list

        self.layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()

        condition_label = QLabel("What needs to happen?")
        left_layout.addWidget(condition_label)

        self.options = QComboBox(self)
        self.options.addItem("Run x times")
        self.options.addItem("Fail detection x times")
        left_layout.addWidget(self.options)

        run_count_label = QLabel("How many times should this happen?")
        self.run_count_input = QLineEdit()
        left_layout.addWidget(run_count_label)
        left_layout.addWidget(self.run_count_input)

        self.action_list = CustomDraggableList(self, [self.actions])

        try:
            if current_setup[0] < 0:
                self.options.setCurrentIndex(1)
            self.run_count_input.setText(str(abs(current_setup[0])))
            self.actions = current_setup[1]
            self.update_action_list()
        except IndexError:
            pass

        left_layout.addWidget(self.action_list)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_action)
        left_layout.addWidget(save_button)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.main_app.switch_to_main_view)
        left_layout.addWidget(back_button)

        right_layout = QVBoxLayout()

        add_actions_label = QLabel("Pick what you'd like to have happen")
        right_layout.addWidget(add_actions_label)

        action_layout = self.main_app.generate_action_list(self)
        right_layout.addWidget(action_layout)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        left_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.layout.addWidget(left_widget)
        self.layout.addWidget(right_widget)

    def switch_to_main_view(self):
        """
        Returns to the main UI from wherever it was previously. If there's an event loop waiting for
        the UI to finish, this also quits it
        """
        self.main_app.central_widget.setCurrentWidget(self)

    def add_action(self, action):
        self.actions.append(action)
        self.update_action_list()

    def update_action_list(self):
        """
        Refreshes the action list with all actions in actions so that all actions are visible to the user
        """
        self.action_list.clear()
        for action in self.actions:
            item = QListWidgetItem(str(action))
            item.setData(QtCore.Qt.ItemDataRole.UserRole, action)
            self.action_list.addItem(item)

    def save_action(self):
        user_input = self.run_count_input.text()
        try:
            if int(user_input) > 0:
                count = int(user_input)
                if self.options.currentText() == "Fail detection x times":
                    count *= -1
                self.main_app.save_meta_modifiers(count, self.actions)
                self.main_app.switch_to_main_view()
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please input a positive integer")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please input a positive integer")

    def get_macro_list(self):
        return self.main_app.macro_list

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
            action = self.actions.pop(self.action_list.start_pos)
            self.actions.insert(end_pos, action)
        super(QListWidget, self.action_list).dropEvent(event)
        self.update_action_list()
