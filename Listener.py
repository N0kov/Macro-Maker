from pynput.keyboard import Key, Listener


running = False
listener = None
callback = None
hotkey = [Key.f8]


def change_hotkey(new_hotkey):
    global hotkey
    hotkey = []
    for key in new_hotkey:
        if len(key) > 1:
            hotkey.append(getattr(Key, key))
        else:
            hotkey.append(key)


def on_press(key):
    global running, listener
    try:
        if key == hotkey[0]:  # Currently only single keys are allowed, as I don't know how to process multiple
            running = False
            if listener is not None:
                stop_listener()
                if callback:  # For if we're doing threading
                    callback()
                return False
    except Exception as e:  # Very occasional X11 errors seem to happen that don't break anything, but it's better
        print("In on_press, " + str(e) + " happened")  # to not have them happen. Same goes for stop_listener


def stop_listener():
    global listener
    try:
        if listener is not None:
            listener.stop()
            listener = None
    except Exception as e:
        print("In stop_listener, " + str(e) + " happened")


def start_listener(script=None):
    global listener, running, callback
    running = True
    if script is not None:
        callback = script  # If we're threading use this
    listener = Listener(on_press=on_press)
    listener.start()


def continue_script():
    global running
    return running


def wait_for_key_press():
    start_listener()
    while continue_script():
        pass
    stop_listener()
