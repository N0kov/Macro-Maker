from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QDialogButtonBox
from PyQt6 import QtCore



class RunCountPopup(QDialog):
    """
    The popup so the user can set a custom run count for the macro. Their input must be an integer greater than zero
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Run count")
        self.setGeometry(550, 300, 270, 170)

        layout = QVBoxLayout()

        self.run_label = QLabel("Enter the amount of times the script should run")
        layout.addWidget(self.run_label)

        self.run_input = QLineEdit()
        layout.addWidget(self.run_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        button_box.accepted.connect(self.check_run_input_validity)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self.installEventFilter(self)
        self.runs = None

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Type.KeyPress and event.key() == QtCore.Qt.Key.Key_Escape:
            self.reject()
        return super(RunCountPopup, self).eventFilter(source, event)

    def check_run_input_validity(self):
        """
        When the user presses "ok", this checks tha they've entered a valid value (an integer greater than zero)
        If so, it returns to main. Otherwise, it notifies the user and stays up
        """
        self.runs = self.run_input.text()
        if self.runs is not None:
            try:
                self.runs = int(self.runs)
                if self.runs > 0:
                    super().accept()
            except ValueError:
                pass

            self.run_label.setText("Enter the amount of times the script should run."
                                   "\n\nThis must be a positive integer")
