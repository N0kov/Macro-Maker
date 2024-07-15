from ImageDetect import compare_main, get_image_not_np
from Listener import wait_for_key_press
from PIL import Image as PILImage
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from pynput.mouse import Controller
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class Image:

    def __init__(self, top_left=None, bottom_right=None, image=None):
        if top_left is None or bottom_right is None:
            print("Setting the coordinates for the image.")
            print("Move your mouse to the top left of the image. Press shift when ready. ", end="")
            wait_for_key_press()
            top_left = list(Controller().position)

            print("\nMove your mouse to the bottom right of the image. Press shift when ready. ", end="")
            wait_for_key_press()
            bottom_right = list(Controller().position)

        check_sizes(top_left, bottom_right)
        self.coordinates = [[top_left[0], top_left[1]], [bottom_right[0], bottom_right[1]]]

        if image is None:
            print("\nPress shift when you are ready to capture image. ", end="")
            wait_for_key_press()
            print()
            self.image = get_image_not_np(self.coordinates)
            self.image_pil = PILImage.fromarray(np.array(self.image))  # Store the PIL image for PyQt display
        else:
            self.image = image

        image_qt = QtGui.QImage(self.image.tobytes(), self.image.width, self.image.height,
                                self.image.width * 3, QtGui.QImage.Format_RGB888)

        self.image = np.array(self.image)
        self.pixmap = QPixmap.fromImage(image_qt)

    def run(self):
        return compare_main(self.image, self.coordinates)

    def get_image(self):
        return self.pixmap


def check_sizes(top_left, bottom_right):
    for index in range(len(top_left)):
        if top_left[index] > bottom_right[index]:
            temp = top_left[index]
            top_left[index] = bottom_right[index]
            bottom_right[index] = temp


class ImageConfigView(QtWidgets.QWidget):
    def __init__(self, main_app, parent=None):
        super(ImageConfigView, self).__init__(parent)
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Configure image")
        self.layout.addWidget(self.label)

        self.present_absent_label = QLabel("Select Click Type:")
        self.layout.addWidget(self.present_absent_label)
        self.present_absent_combo = QComboBox()
        self.present_absent_combo.addItems(["Present", "Absent"])
        self.layout.addWidget(self.present_absent_combo)

        self.top_left_label = QLabel("Press shift to set the top left of the image to where your mouse is.")
        self.layout.addWidget(self.top_left_label)

        self.top_left_display = QLabel("Top left: Not set")
        self.layout.addWidget(self.top_left_display)

        self.bottom_right_label = QLabel("Press control to set the bottom right"
                                              " of the image to where your mouse is.")
        self.layout.addWidget(self.bottom_right_label)

        self.bottom_right_display = QLabel("Bottom right: Not set")
        self.layout.addWidget(self.bottom_right_display)

        self.captured_image_label = QLabel("Press alt to capture an image once the top left and bottom right are set")
        self.layout.addWidget(self.captured_image_label)

        self.captured_image_display = QLabel("No image captured")
        self.layout.addWidget(self.captured_image_display)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_action)
        self.layout.addWidget(self.save_button)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.main_app.switch_to_main_view)
        self.layout.addWidget(self.back_button)

        self.top_left = None
        self.bottom_right = None
        self.image = None
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Shift:
            self.top_left = list(Controller().position)
            self.top_left_display.setText("Top left at: " + str(self.top_left))
            return True
        elif event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Control:
            self.bottom_right = list(Controller().position)
            self.bottom_right_display.setText("Coordinates: " + str(self.bottom_right))
            return True

        if self.top_left and self.bottom_right:
            if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Alt:
                check_sizes(self.top_left, self.bottom_right)

                self.image = get_image_not_np([[self.top_left[0], self.top_left[1]],
                                               [self.bottom_right[0], self.bottom_right[1]]])

                # To QPixmap
                image_qt = QtGui.QImage(self.image.tobytes(), self.image.width, self.image.height,
                                        self.image.width * 3, QtGui.QImage.Format_RGB888)

                pixmap = QPixmap.fromImage(image_qt)

                max_width = 600
                max_height = 400

                scaled_pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                self.captured_image_display.setPixmap(scaled_pixmap)

        return super(ImageConfigView, self).eventFilter(obj, event)

    def save_action(self):
        # Save configured action
        top_left = self.top_left
        bottom_right = self.bottom_right
        image = self.image
        present_or_not = self.present_absent_combo.currentText().lower()[0]
        if np.all(top_left and bottom_right and image):
            print("OK")
            check_sizes(top_left, bottom_right)
            condition = Image(top_left, bottom_right, image)
            self.main_app.add_condition(condition, present_or_not)
        self.main_app.switch_to_main_view()
