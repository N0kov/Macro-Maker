from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidgetItem, QMenu, QPushButton, QComboBox
from copy import deepcopy

from actions import *


def right_click_actions_menu(position, source):
    """
    The menu for right-clicking on an action or condition. It creates a clickable dropdown menu, that allows the
    user to copy an item, edit one or delete the item.
    :param position: The QPoint x,y coordinates that the user's mouse was at when the right-clicked on the item
    :param source: The app that sent this request
    """
    sender = source.sender()
    menu = QMenu()
    copy_item = menu.addAction("Copy")
    edit_the_item = menu.addAction("Edit")
    remove_item = menu.addAction("Remove")

    global_position = sender.viewport().mapToGlobal(position)
    selected_action = menu.exec(global_position)
    item = sender.itemAt(position)
    if item is not None:
        item_data = item.data(Qt.ItemDataRole.UserRole)

        if selected_action == remove_item:
            copy_or_remove_item(source, sender.row(item), "pop")

        elif selected_action == copy_item:
            copy_or_remove_item(source, item_data, "append")

        elif selected_action == edit_the_item:
            edit_item(item_data, source)

        source.update_action_list()


def copy_or_remove_item(source, item, choice):
    """
    Calls the desired method (either append or remove) on the passed in list using the specified item. Does
    nothing if choice is not append or remove
    :param source: The list to be edited - list
    :param item: The item to be copied / removed - anything
    :param choice: What the user wants to do - String
    """
    # There are three different things tried here for copy and remove as there are three different possible data
    # types that could be passed in. See dropEvent from CustomDraggableList for a full explanation
    if choice == "append" or choice == "pop":
        if choice == "append":
            item = deepcopy(item)
        try:
            if source.source_list is source.main_application.advanced_actions:
                method = getattr(source.source_list[source.main_application.current_macro][1], choice)
            else:
                method = getattr(source.source_list[source.main_application.current_macro], choice)
        except AttributeError:
            method = getattr(source.source_list[0], choice)
        except ValueError:
            return
        method(item)
    else:
        pass


def edit_item(item, source):
    """
    Opens the item's UI, and alters the chosen item to match what the user edited it to be
    :param item: The item to be edited. Can be an Action, or a QListWidgetItem
    :param source: The app that sent this request
    """
    if QListWidgetItem is type(item):
        item = item.data(Qt.ItemDataRole.UserRole)
    call_ui_with_params(source, item)


def call_ui_with_params(source, item):
    """
    Calls the UI for the specified item, with the current item's data passed in so the user can edit it
    This waits until the UI is closed to allow the script to close
    :param item: The action to be edited
    :param source: The app that sent this request
    """
    if isinstance(item, ClickX):
        edit_view = ClickXUI(source, item)
    elif isinstance(item, MouseTo):
        edit_view = MouseToUI(source, item)
    elif isinstance(item, SwipeXY):
        edit_view = SwipeXyUI(source, item)
    elif isinstance(item, TypeText):
        edit_view = TypeTextUI(source, item)
    elif isinstance(item, Wait):
        edit_view = WaitUI(source, item)
    elif isinstance(item, NudgeMouse):
        edit_view = NudgeMouseUI(source, item)
    elif isinstance(item, TriggerMacro):
        edit_view = TriggerMacroUI(source, source.get_macro_list(), item)
    else:
        return

    # It's possible that one layer above could be calling this, or two layers above (if in AdvancedActions)
    try:
        source.main_application.central_widget.addWidget(edit_view)
        source.main_application.central_widget.setCurrentWidget(edit_view)
    except AttributeError:
        source.main_application.main_app.central_widget.addWidget(edit_view)
        source.main_application.main_app.central_widget.setCurrentWidget(edit_view)


def create_push_button():
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
    return add_action_button


def create_macro_list(macro_list):
    """
    Takes a QComboBox of the possible macros, and adds all of them to a new QComboBox,
    up until it says "Create a macro", where it is then returned
    :param macro_list: A QComboBox. Must have an index which says "Create a macro"
    :return: A QComboBox of items up to Create a macro
    """
    macro_to_remove_box = QComboBox()
    macro_to_remove_box.addItems(create_macro_list_names(macro_list))
    return macro_to_remove_box


def create_macro_list_names(macro_list, remove_index=None):
    i = 0
    macro_names = []
    while macro_list.itemText(i) != "Create a macro":
        macro_names.append(macro_list.itemText(i))
        i += 1
    if remove_index is not None:
        macro_names.pop(remove_index)
    return macro_names
