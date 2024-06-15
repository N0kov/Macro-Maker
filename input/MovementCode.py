import pyinput
import listener
import screenshot
import ImageDetect

def get_coords():
    print("Where should the top left be?")
    print("Press escape when you mouse is at the correct spot.")

    while listener.continue_script():
        pass

    coords = [[pyinput.get_mouse_positon()[0], pyinput.get_mouse_positon()[1]], [0,0]]

    print("\nWhere would you like the bottom right to be? (Escape to confirm)")
    while listener.continue_script():
        pass

    coords = [[coords[0][0], coords[0][1]], [pyinput.get_mouse_positon()[0], pyinput.get_mouse_positon()[1]]]

    print("\nPress enter when ready to capture the reference image:")
    while listener.continue_script():
        pass
    
    reference_image = ImageDetect.get_image(coords)
    print(reference_image.size)

    print("\nPress enter to start image detection")

    while listener.continue_script():
        pass


    ImageDetect.compare_main(reference_image, coords)
    screenshot.take_section()


get_coords()