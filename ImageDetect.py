from PIL import ImageGrab
import numpy as np


# Calculates the mean square error of two numpy array images (image1 and image2), then returns the MSE
# Raises a ValueError if the two images aren't identical in shape
def mse(image1, image2):
    if image1.shape != image2.shape:
        raise ValueError("Images must have the same shape to compute MSE")

    return np.mean((image1 - image2) ** 2)


# Gets the mse of the two passed in numpy images (image1 and image2), if it's less than the given threshold,
# it returns True. Otherwise, returns False
def images_are_similar(image1, image2, threshold):
    error = mse(image1, image2)
    return error <= threshold


# Captures and returns a screenshot of the specified area in RGB format. Coordinates in the form [[x1, y1], [x2, y2]]
# must be passed in, and if nothing is passed into the second field (not_numpy) the image will be returned
# as a np.array. Otherwise, it'll be returned as a PIL image
def get_image(coordinates, not_numpy=None):
    bbox = (coordinates[0][0], coordinates[0][1], coordinates[1][0], coordinates[1][1])
    screenshot = ImageGrab.grab(bbox)
    if screenshot.mode == 'RGBA':
        screenshot = screenshot.convert('RGB')
    if not_numpy is None:
        screenshot = np.array(screenshot)
    return screenshot


# Calculates the threshold of acceptable error for any image passed in. This is based on the width and height of the
# image, with a smaller image will have a smaller threshold
def threshold_calculation(image):
    width, height = image.shape[:2]
    return ((width * height) / 2) ** .15  # This is a semi-arbitrary equation that gave a reasonable seeming value


# Compares two images, returns True if the difference between them is below the given threshold.
# reference_image is a given image that you're comparing what's on screen to. coordinates are a 2D array in the form
# [[x1, y1], [x2, y2]]. Threshold is the upper bound of acceptable error (see threshold_calculation)
def compare_images(reference_image, coordinates, threshold):
    if images_are_similar(get_image(coordinates), reference_image, threshold):
        return True
    return False
