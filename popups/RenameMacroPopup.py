from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QLineEdit
from actions.mouse_shortcuts import create_macro_list


class RenameMacroPopup(QDialog):
    """
    The popup so the user can set a custom run count for the macro. Their input must be an integer greater than zero
    """

    def __init__(self, macro_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rename a Macro")
        self.setGeometry(550, 300, 300, 200)

        layout = QVBoxLayout()

        removal_label = QLabel("Pick the macro you'd like to rename")
        layout.addWidget(removal_label)

        self.macro_choice_box = create_macro_list(macro_list)
        layout.addWidget(self.macro_choice_box)

        rename_label = QLabel("Enter the new name")
        layout.addWidget(rename_label)

        self.new_name = QLineEdit()
        layout.addWidget(self.new_name)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.runs = None

    def get_macro_choice(self):
        return self.macro_choice_box.currentIndex()

    def get_new_name(self):
        return self.new_name.text()
