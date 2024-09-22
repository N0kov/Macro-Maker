from PyQt6.QtWidgets import QListWidget
import PyQt6.QtCore as QtCore
from misc_utilities import UI_helper


class CustomDraggableList(QListWidget):
    """
    A QListWidget that comes with functions to be able to drag items around and update their associated lists
    (responsible for the items in the QListWidget), and right click on them, allowing copying, deletion and
    editing of the items inside, while also updating their base lists
    """

    def __init__(self, main_application, source_list):
        """
        Sets the functionality for the list, adds the connections on clicking and dragging / dropping
        :param main_application: The parent application of the QListWidget
        :param source_list: The list that's responsible for creating the elements of the QListWidget
        """
        super().__init__()

        self.main_application = main_application
        self.source_list = source_list

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)  # Right click
        self.customContextMenuRequested.connect(lambda position: UI_helper.right_click_actions_menu(position, self))

        self.itemDoubleClicked.connect(lambda item: UI_helper.edit_item(item, self))  # Double click = edit
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)  # Dragging
        self.start_pos = None
        self.startDrag = self.startDrag
        self.dropEvent = self.dropEvent

    def startDrag(self, supportedActions):  # camelCase to match with PyQt6's def
        """
        Overwrites the startDrag def from PyQt5 to record the original row of the item that's being dragged and the item
        itself. Then calls the standard startDrag to drag the item. This is used for the actions list
        :param supportedActions: The default actions that are supported by PyQt5's start drag definition, here because
            supportedActions is a default parameter for the def
        """
        self.start_pos = self.currentRow()
        self.dragged_item = self.currentItem()
        super().startDrag(supportedActions)

    def dropEvent(self, event):  # camelCase to match with PyQt6's def
        """
        Overwrites the dropEvent def from PyQt5. It still moves the UI element to the new position, but additionally
        moves the action object in self.action_list to the new position to permanently make the switch and have the
        macro run in the correct order
        :param event: The menu item that's dropped. A default parameter that comes with dropEvent from PyQt5
        """
        end_pos = self.indexAt(event.position().toPoint()).row()

        if end_pos == -1:
            end_pos = self.count()
        elif event.position().toPoint().y() < self.visualItemRect(self.item(0)).top():
            end_pos = 0

        if self.dragged_item:
            # The problem is that all of these lists are using different data types, so it needs to account for each
            # one. If it's coming from actions, it's [[]], advanced_actions in main is [["item", ["a", "b"]]],
            # AdvancedActions is [], and all three need to be checked for. AdvancedActions is being passed in wrapped
            # in a [], to make it compatible with the other two, so it's format is [[]], with all data in index [0][x]
            if self.source_list == self.main_application.actions:
                list_to_use = self.source_list[self.main_application.current_macro]
            elif self.source_list[0] == self.main_application.actions:
                list_to_use = self.source_list[0]
            else:
                list_to_use = self.source_list[self.main_application.current_macro][1]

            action = list_to_use.pop(self.start_pos)
            list_to_use.insert(end_pos, action)

        super().dropEvent(event)
        self.update_action_list()

    def update_action_list(self):
        """
        This gets implicitly called in several places, refreshes the items in the actions list,
        and also the advanced actions list
        """
        self.main_application.update_action_list()
        try:
            self.main_application.update_advanced_action_list()
        except AttributeError:
            pass

    def switch_to_main_view(self):
        """
        This gets implicitly called at the end of editing actions,
        calls the main app's method to switch to the main view
        """
        self.main_application.switch_to_main_view()
