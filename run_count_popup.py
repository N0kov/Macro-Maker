from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QDialogButtonBox


class RunCountPopup(QDialog):
    """
    The popup so the user can set a custom run count for the macro. Their input must be an integer greater than zero
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Run count")
        self.setGeometry(550, 300, 270, 170)

        self.layout = QVBoxLayout()

        self.run_label = QLabel("Enter the amount of times the script should run")
        self.layout.addWidget(self.run_label)

        self.run_input = QLineEdit()
        self.layout.addWidget(self.run_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.check_run_input_validity)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

        self.runs = None

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

