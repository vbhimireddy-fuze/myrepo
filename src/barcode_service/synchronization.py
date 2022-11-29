# coding=utf-8
from threading import Lock
from typing import Callable

__all__ = (
    "ShutDownSignal",
)

class ShutDownSignal:
    def __init__(self):
        self.__lock = Lock()
        self.__callbacks_list = []

    def send_signal(self) -> None:
        with self.__lock:
            for cb in self.__callbacks_list:
                cb()

    def register_callback(self, cb: Callable[[], None]) -> None:
        with self.__lock:
            self.__callbacks_list.append(cb)
