from pynput.keyboard import Key, Listener, KeyCode


# Base parameters
listener = None  # Is the listener active?
callback = None  # Callback function
hotkey = []  # The keys that are being listened for
break_key = Key.f10
break_key_str = 'f10'


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
    """
    Removes the hotkey at the specified index from the hotkey list
    """
    global hotkey
    hotkey.pop(index)


def set_break_key(new_break_key):
    global break_key, break_key_str
    break_key_str = new_break_key
    break_key = convert_to_pynput(new_break_key)


def convert_to_pynput(keys):
    """
    Attempts to convert the passed in string to pynput form. If it isn't valid, an empty string is returned instead
    :param keys: The string to be processed
    :return: The pynput form of keys / an empty string if invalid
    """
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
        elif key == break_key:
            callback(-1)
    except Exception as e:
        pass


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
    """
    Calls the callback function at the index passed in, and stops the listener
    :param index: The index that should be called
    """
    if listener is not None:
        listener.stop()
        if callback:  # For if we're doing threading
            callback(index)


def stop_listener():
    """
    Stops the listener
    """
    if listener is not None:
        listener.stop()
