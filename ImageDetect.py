from PIL import Image
from PIL import ImageGrab
import numpy as np


def load_image(image_path):
    return Image.open(image_path)


def mse(image1, image2):
    if image1.shape != image2.shape:
        dimensions(image1)
        dimensions(image2)
        raise ValueError("Images must have the same shape to compute MSE")

    return np.mean((image1 - image2) ** 2)


def images_are_similar(image1, image2):
    error = mse(image1, image2)
    return error <= threshold_calculation(image1)


def dimensions(image):
    width, height = image.shape[:2]
    print()
    print(width)
    print(height)


def get_image(coords):
    bbox = (coords[0][0], coords[0][1], coords[1][0], coords[1][1])
    screenshot = ImageGrab.grab(bbox)
    if screenshot.mode == 'RGBA':
        screenshot = screenshot.convert('RGB')
    return np.array(screenshot)


def get_image_not_np(coords):           # replace at some point to be the de facto one
    bbox = (coords[0][0], coords[0][1], coords[1][0], coords[1][1])
    screenshot = ImageGrab.grab(bbox)
    if screenshot.mode == 'RGBA':
        screenshot = screenshot.convert('RGB')
    return screenshot


def threshold_calculation(image):
    width, height = image.shape[:2]
    return ((width * height) / 2) ** .15


def load_the_image(image_path):
    image = Image.open(image_path)
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    return np.array(image)


def compare_images(test_image, reference_image):
    if images_are_similar(test_image, reference_image):
        return True
    return False


def compare_main(reference_image, coords):
    return compare_images(np.array(reference_image), get_image(coords))
