from pynput.keyboard import Key, Listener, KeyCode


# Base parameters
running = False  # Is it running?
listener = None  # Is the listener active?
callback = None  # Callback function
hotkey = [Key.f8]  # The key that's being listened for



def change_hotkey(new_hotkey):
    """
    Changes the hotkey that the listener is listening for. Will throw an AttributeError exception
    if the passed in string isn't valid for pynput. If it isn't valid, or if an empty array is passed in,
    hotkey will be set to an empty array
    :param new_hotkey: The new hotkey for the listener to listen for. This must be a string that is processable by
        pynput (i.e. should work as Key.something)
    :return:
    """
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


def on_press(key):
    """
    Listens for when the user presses the key specified in hotkey is pressed. This is only listening for the first value
    It stops the listener, and if a callback has been specified it'll trigger the callback
    except Exception is here if any bad data gets passed in. As large quantities of unknown keyboard data goes through
    on_press, it's good to be better safe than sorry
    :param key: A key that the user pressed. Must be in pynput form
    """
    global running, listener
    try:
        if key == hotkey[0]:  # Currently only single keys are allowed, as I don't know how to process multiple
            running = False
            if listener is not None:
                listener.stop()
                if callback:  # For if we're doing threading
                    callback()
    except Exception as e:
        pass


def start_listener(script=None):
    """
    This starts the listener. script=None allows a callback a script or definition to be called when the listener stops
    All keyboard inputs get sent to on_press
    :param script: A script or definition. Said script / def does not need to be imported to Listener
    """
    global listener, running, callback
    running = True
    if script is not None:
        callback = script  # If we're threading, sets a callback
    listener = Listener(on_press=on_press)
    listener.start()


def wait_for_key_press():
    """
    This is an encapsulated variant to pause the thread and wait for when the hotkey is pressed and then stop the
    listener, effectively resuming the thread
    """
    start_listener()
    while running:
        pass
    listener.stop()
