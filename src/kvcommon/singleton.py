from abc import ABCMeta, abstractmethod

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

"""
Example:

class MySingleton(metaclass=SingletonMeta):
    pass
"""

class AbstractSingleton(SingletonMeta, ABCMeta):
    pass
