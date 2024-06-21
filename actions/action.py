from abc import ABC, abstractmethod


class Action(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def __str__(self):
        pass
