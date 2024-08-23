from pynput.keyboard import Key, Listener, KeyCode


# Base parameters
listener = None  # Is the listener active?
callback = None  # Callback function
hotkey = []  # The keys that are being listened for


def change_hotkey(new_hotkey, hotkey_index):
    """
    Changes the hotkey that the listener is listening for / adds a new hotkey to listen for.
    If it isn't valid, or if an empty array is passed in, hotkey will be set to an empty array
    :param new_hotkey: The new hotkey for the listener to listen for. This must be a string that is processable by
        pynput (i.e. should work as Key.something)
    :param hotkey_index: The index that the hotkey should be inserted at
    """
    global hotkey
    if hotkey_index < len(hotkey):
        hotkey[hotkey_index] = convert_to_pynput(new_hotkey)
    else:
        hotkey.append(convert_to_pynput(new_hotkey))


def remove_hotkey(index):
    global hotkey
    hotkey.pop(index)


def convert_to_pynput(keys):
    try:
        if len(keys) > 1:
            return getattr(Key, keys)
        else:
            return KeyCode.from_char(keys)
    except AttributeError:
        return ""


def on_press(key):
    """
    Listens for when the user presses the key specified in hotkey is pressed. This is only listening for the first value
    It stops the listener, and if a callback has been specified it'll trigger the callback
    except Exception is here if any bad data gets passed in. As large quantities of unknown keyboard data goes through
    on_press, it's good to be better safe than sorry
    :param key: A key that the user pressed. Must be in pynput form
    """
    global listener
    try:
        if key in hotkey:  # Currently only single keys are allowed, as I don't know how to process multiple
            if listener is not None:
                listener.stop()
                if callback:  # For if we're doing threading
                    callback(hotkey.index(key))
    except Exception as e:
        print("on_press exception: " + str(e))


def start_listener(script=None):
    """
    This starts the listener. script=None allows a callback a script or definition to be called when the listener stops
    All keyboard inputs get sent to on_press
    :param script: A script or definition. Said script / def does not need to be imported to Listener
    """
    global listener, callback
    if script is not None:
        callback = script  # If we're threading, sets a callback
    listener = Listener(on_press=on_press)
    listener.start()


def trigger_by_index(index):
    try:
        if listener is not None:
            listener.stop()
            if callback:  # For if we're doing threading
                callback(index)
    except Exception as e:
        listener.stop()


def stop_listener():
    if listener is not None:
        listener.stop()