from image_similarity_detector import compare_images, threshold_calculation, get_image as capture_image
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from pynput.mouse import Controller
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class ImageCondition:
    """
    Holds a copy of a captured image. It takes coordinates and an image, can be run to see if the image it has is
    the same as what's on screen and can return the current image
    """

    def __init__(self, top_left, bottom_right, image):
        check_sizes(top_left, bottom_right)
        self.coordinates = [[top_left[0], top_left[1]], [bottom_right[0], bottom_right[1]]]

        self.image = image

        image_qt = QtGui.QImage(self.image.tobytes(), self.image.width, self.image.height,
                                self.image.width * 3, QtGui.QImage.Format_RGB888)

        self.image = np.array(self.image)
        self.image_pixmap = QPixmap.fromImage(image_qt)

        self.threshold = threshold_calculation(self.image)

    def run(self):
        """
        Checks if the image ImageCondition has is very similar to what's on screen Returns True if so, False otherwise.
            They don't need to be an exact match
        :return: True if what's on screen is very similar to the reference image, False otherwise
        """
        return compare_images(self.image, self.coordinates, self.threshold)


def check_sizes(top_left, bottom_right):
    """
    Checks that the coordinates of top_left are both up and to the left of bottom_right. Both in the form [x, y].
    For example, top_left: [30, 500], bottom_right: [100, 200] would be changed to [30, 200] and [100, 500] respectively
    :param top_left: The top left x, y coordinates in list form. Either float or bool
    :param bottom_right: The bottom right x, y coordinates in list form. Either float or bool
    """
    for index in range(len(top_left)):
        if top_left[index] > bottom_right[index]:
            temp = top_left[index]
            top_left[index] = bottom_right[index]
            bottom_right[index] = temp


class ImageConfigView(QtWidgets.QWidget):
    """
    The UI handler for the Image Class. Allows the user to select if the image should be present or absent, and then
    pick the coordinates of it and take the screenshot which is displayed to the user. It's then returned to UI3 in
    the form of an Image object
    """

    def __init__(self, main_app, parent=None):
        self.top_left_temp = None  # The temp ones are needed throughout, so they're class vars. These are needed
        self.bottom_right_temp = None  # as after taking a screenshot the user should still be able to change the
        self.top_left_permanent = None  # coordinates, but to make ImageDetect the final ones must be the same as
        self.bottom_right_permanent = None  # those in the screenshot. permanent = temp on taking a screenshot
        self.image = None

        super(ImageConfigView, self).__init__(parent)
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        """
        Initializes the UI
        """
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

        self.installEventFilter(self)

    def eventFilter(self, source, event):
        """
        Processes when shift and control are hit (for top left and bottom right) and saves the mouse positions.
        When both are valid, hitting alt takes a screenshot of the selected area and displays it in the UI
        Returns True if the user pressed shift, control or successfully takes a screenshot. Returns to the default
        eventFilter handling otherwise
        :param source: The source of the event - not used, only present as it is a set field
        :param event: The thing that happened to the UI
        :return: True if the user pressed shift, control or successfully takes a screenshot. Reverts to the standard
            eventFilter handling otherwise
        """
        if (event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Shift):
            self.top_left_temp = list(Controller().position)
            self.top_left_display.setText("Top left at: " + str(self.top_left_temp))
            return True
        elif (event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Control):
            self.bottom_right_temp = list(Controller().position)
            self.bottom_right_display.setText("Bottom right at: " + str(self.top_left_temp))
            return True

        if self.top_left_temp and self.bottom_right_temp:
            if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Alt:
                check_sizes(self.top_left_temp, self.bottom_right_temp)

                self.top_left_permanent = self.top_left_temp
                self.bottom_right_permanent = self.bottom_right_temp

                self.image = capture_image([[self.top_left_permanent[0], self.top_left_permanent[1]],
                                            [self.bottom_right_permanent[0], self.bottom_right_permanent[1]]],
                                           "not numpy array")

                image_qt = QtGui.QImage(self.image.tobytes(), self.image.width, self.image.height,
                                        self.image.width * 3, QtGui.QImage.Format_RGB888)

                pixmap = QPixmap.fromImage(image_qt)
                scaled_pixmap = pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.captured_image_display.setPixmap(scaled_pixmap)
                return True

        return super(ImageConfigView, self).eventFilter(source, event)

    def save_action(self):
        """
        For when save is pressed. Creates a new Image object from the pre-established coordinates and image, and
        returns to the main UI view, alongside if the image should be present or not. If there are no coordinates or no
        an image, nothing happens.
        Does nothing if save is pressed without the coordinates and an image being present
        :return: An ImageCondition from the established data is created and sent back to UI3, alongside if the
        image should be present or not. If anything is missing (one of the coordinates or the image), nothing happens
        """
        top_left = self.top_left_permanent
        bottom_right = self.bottom_right_permanent
        image = self.image
        present_or_not = self.present_absent_combo.currentText().lower()[0]
        if top_left and bottom_right and image:
            check_sizes(top_left, bottom_right)
            condition = ImageCondition(top_left, bottom_right, image)
            self.main_app.add_condition(condition, present_or_not)
            self.main_app.switch_to_main_view()
