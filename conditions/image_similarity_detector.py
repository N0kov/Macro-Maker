from PIL import ImageGrab
import numpy as np


def mse(image1, image2):
    """
    Calculates the mean square error of two numpy array images (image1 and image2), then returns the MSE
    Raises a ValueError if the two images aren't identical in shape. They both must be in RGB form
    :param image1: The reference image. Must be an RGB image converted to a numpy array
    :param image2: The text image. Must be a numpy array
    :return: A float, the MSE of the difference between the two images
    """
    if image1.shape != image2.shape:
        raise ValueError("Images must have the same shape to compute MSE")

    return np.mean((image1 - image2) ** 2)


def images_are_similar(image1, image2, threshold):
    """
    Gets the mse of the two passed in numpy images (image1 and image2), if it's less than or equal
    to than the given threshold it returns True. Otherwise, returns False.
    :param image1: The reference image. Must be an RGB image converted to a numpy array
    :param image2: The text image. Must be an RGB image converted to a numpy array
    :param threshold: An int or float that represents the maximum allowable MSE of the two images
    :return: Bool, True if the error is less than or equal to the threshold, False otherwise
    """
    error = mse(image1, image2)
    return error <= threshold


def get_image(coordinates, not_numpy=None):
    """
    Captures and returns a screenshot of the specified area in RGB format. Coordinates in the form [[x1, y1], [x2, y2]]
    must be passed in, and if nothing is passed into the second field (not_numpy) the image will be returned
    as a np.array. Otherwise, it'll be returned as a PIL image. They will first be converted to RGB
    :param coordinates: A 2D array in the form [[x1, y1,], [x2, y2]] (initial position, final position). Must be ints
    :param not_numpy: A flag. If empty, the image will be converted to a np array. If anything is passed in, it won't
        be converted
    :return: The screenshot of the specified area. If there is not a flag, it will be in PIL form, if there is it will
        be a numpy array. Either way it will be in RGB form, not RGBA
    """
    bbox = (coordinates[0][0], coordinates[0][1], coordinates[1][0], coordinates[1][1])
    screenshot = ImageGrab.grab(bbox)
    if screenshot.mode == 'RGBA':
        screenshot = screenshot.convert('RGB')
    if not_numpy is None:
        screenshot = np.array(screenshot)
    return screenshot


def compare_images(reference_image, coordinates, threshold):
    """
    Compares two images, returns True if the difference between them is below the given threshold.
    reference_image is a given image that you're comparing what's on screen to. coordinates are a 2D array in the form
    [[x1, y1], [x2, y2]]. Threshold is the upper bound of acceptable error (see threshold_calculation)
    The dimensions of the coordinates and the image must be the same, and (x1, y1) must be in the coordinates of the top
    left of the reference image
    :param reference_image: An RGB image in the form of a numpy array
    :param coordinates: 2D array in the form [[x1, y1], [x2, y2]]. (x1, y1) must be in the top left of where the
        reference image was captured, and the dimensions must be identical to the reference image
    :param threshold: Float, the maximum allowable difference between what's on screen and the reference image
    :return: True if the MSE of the two images is less than the threshold, false otherwise
    """
    if images_are_similar(get_image(coordinates), reference_image, threshold):
        return True
    return False
