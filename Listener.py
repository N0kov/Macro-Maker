from pynput.keyboard import Key, Listener

running = True
listener = None

def on_press(key):
    global running, listener
    try:
        if key == Key.shift:
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

def continue_script():
    global running
    return running

start_listener()
