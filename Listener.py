from pynput.keyboard import Key, Listener, KeyCode


# Base parameters
running = False  # Is it running?
listener = None  # Is the listener active?
callback = None  # Callback function
hotkey = [Key.f8]  # The key that's being listened for


# Changes the hotkey that the listener is listening for. This must be a string that is valid to be processed by pynput.
# except AttributeError handles if it isn't. If it isn't valid, or if an empty array is passed in,
# hotkey will be set to an empty array
def change_hotkey(new_hotkey):
    global hotkey
    hotkey = []
    try:
        for key in new_hotkey:
            if len(key) > 1:
                hotkey.append(getattr(Key, key))
            else:
                hotkey.append(KeyCode.from_char(key))
    except AttributeError:
        pass


# Listens for when the user presses the key specified in hotkey is pressed. This is only listening for the first value
# It stops the listener, and if a callback has been specified it'll trigger the callback
# except Exception is here if any bad data gets passed in. As large quantities of unknown keyboard data goes through
# on_press, it's good to be better safe than sorry
def on_press(key):
    global running, listener
    try:
        if key == hotkey[0]:  # Currently only single keys are allowed, as I don't know how to process multiple
            running = False
            if listener is not None:
                listener.stop()
                if callback:  # For if we're doing threading
                    callback()
                return False
    except Exception as e:
        pass


# This starts the listener. script=None allows a callback a script to be called when the listener stops
# All keyboard inputs get sent to on_press
def start_listener(script=None):
    global listener, running, callback
    running = True
    if script is not None:
        callback = script  # If we're threading use this
    listener = Listener(on_press=on_press)
    listener.start()


# This is an encapsulated variant to pause the thread and wait for when the hotkey is pressed and then stop the
# listener, effectively resuming the thread
def wait_for_key_press():
    start_listener()
    while running:
        pass
    listener.stop()
