from abc import ABC, abstractmethod


class Action(ABC):
    """
    An abstract base class, used by click_x, mouse_to, swipe_xy, type_text and wait. All of them need to have an init
    and str definition that overwrite the built-in ones. They also need to have a run() that can run what's inside
    of them
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def run(self):
        pass

