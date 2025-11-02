from abc import ABCMeta, abstractmethod
import threading


class SingletonMeta(type):
    _instances = {}

    # A class-level lock to guard against race conditions during initialization
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        
        # Double-checked lock
        if cls not in cls._instances:
            with cls._lock:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


"""
Example:

class MySingleton(metaclass=SingletonMeta):
    pass
"""


class AbstractSingleton(SingletonMeta, ABCMeta):
    pass
