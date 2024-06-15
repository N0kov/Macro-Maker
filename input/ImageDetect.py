from PIL import Image
from PIL import ImageGrab
import numpy as np

top_left = [93, 116]

def load_image(image_path):
    return Image.open(image_path)

def mse(image1, image2):
    np_image1 = np.array(image1)
    np_image2 = np.array(image2)

    if np_image1.shape != np_image2.shape:
        dimensions(image1)
        dimensions(image2)
        raise ValueError("Images must have the same shape to compute MSE")

    return np.mean((np_image1 - np_image2) ** 2) #MSE

def images_are_similar(image1, image2):
    error = mse(image1, image2)
    print ("Error: " + str(error))
    return error <= threshold_calculation(image1)

def dimensions(image):
    width, height = image.size
    print()
    print(width)
    print(height)

def get_image(coords):
    bbox = (coords[0][0], coords[0][1], coords[1][0], coords[1][1])
    screenshot = ImageGrab.grab(bbox)
    if screenshot.mode == 'RGBA':
        screenshot = screenshot.convert('RGB')
    return screenshot

def threshold_calculation(image):
    width, height = image.size
    return ((width * height) / 2) ** .15

def load_the_image(image_path):
    image = Image.open(image_path)
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    return image

def compare_images(test_image, reference_image):
    if images_are_similar(test_image, reference_image):
        print("Match found")
        return True
    return False
    # else:
    #     print("Images are not similar enough")

def compare_main(reference_image, coords):
    error_threshold = threshold_calculation(reference_image)
    print("Threshold: " + str(error_threshold))
    while not compare_images(reference_image, get_image(coords)):
        pass
