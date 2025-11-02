import time
import typing as t


class JobTimer:
    _start_time: float = -1.0
    _started: bool = False
    _callback_start: t.Callable | None = None
    _callback_stop: t.Callable[[float], None]

    def __init__(
            self,
            stop_callback: t.Callable[[float], None],
            start_callback: t.Callable | None = None,
        ) -> None:
        self._callback_start = start_callback
        self._callback_stop = stop_callback

    def start(self):
        if self._callback_start:
            self._callback_start()
        self._start_time = time.time()
        self._started = True

    def stop(self):
        if not self._started:
            return
        duration = time.time() - self._start_time
        self._callback_stop(duration)
