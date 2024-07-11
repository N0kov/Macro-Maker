from pynput.keyboard import Key, Listener

running = False
listener = None

hotkey = Key.f8


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
        if key == hotkey:
            running = False
            if listener is not None:
                listener.stop()
                return False
    except AttributeError:
        pass


def start_listener():
    global listener, running
    running = True
    listener = Listener(on_press=on_press)
    listener.start()


def stop_listener():
    global listener
    if listener is not None:
        listener.stop()
        listener = None


def continue_script():
    global running
    return running


def wait_for_shift_press():
    start_listener()
    while continue_script():
        pass
    stop_listener()
