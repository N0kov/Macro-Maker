from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QDialogButtonBox


class RunCountPopup(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Run count")
        self.setGeometry(650, 450, 300, 180)

        self.layout = QVBoxLayout()

        self.run_label = QLabel("Enter the amount of times the script should run")
        self.layout.addWidget(self.run_label)

        self.run_input = QLineEdit()
        self.layout.addWidget(self.run_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

        self.runs = None

    def accept(self):
        self.runs = self.run_input.text()
        if self.runs is not None:
            try:
                self.runs = int(self.runs)
                if int(self.runs > 0):
                    super().accept()
            except ValueError:
                pass

            self.run_label.setText("Enter the amount of times the script should run."
                                   "\n\nThis must be a positive integer")
            print("set")
