from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from misc_utilities.UI_helper import create_macro_list


class RemoveMacroPopup(QDialog):
    """
    The popup so the user can set a custom run count for the macro. Their input must be an integer greater than zero
    """

    def __init__(self, macro_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Remove a Macro")
        self.setGeometry(550, 300, 270, 170)

        layout = QVBoxLayout()

        removal_label = QLabel("Pick the macro you would like to remove")
        layout.addWidget(removal_label)

        self.macro_to_remove_box = create_macro_list(macro_list)
        layout.addWidget(self.macro_to_remove_box)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.runs = None

    def get_macro_to_remove(self):
        return self.macro_to_remove_box.currentIndex()
