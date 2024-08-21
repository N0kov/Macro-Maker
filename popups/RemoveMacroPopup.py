from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QDialogButtonBox


class RemoveMacroPopup(QDialog):
    """
    The popup so the user can set a custom run count for the macro. Their input must be an integer greater than zero
    """

    def __init__(self, macro_list: QComboBox, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Remove a Macro")
        self.setGeometry(550, 300, 270, 170)

        layout = QVBoxLayout()

        removal_label = QLabel("Pick the macro you would like to remove")
        layout.addWidget(removal_label)

        i = 0
        self.macro_to_remove_box = QComboBox()
        while macro_list.itemText(i) != "Create a macro":
            self.macro_to_remove_box.addItem(macro_list.itemText(i))
            i += 1
        layout.addWidget(self.macro_to_remove_box)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.runs = None

    def get_macro_to_remove(self):
        return self.macro_to_remove_box.currentIndex()
