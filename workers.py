import threading
import time
from typing import Callable, Optional

class stoppable_worker:
    def __init__(self, target: Callable[[threading.Event], None],
                 name: Optional[str] = None, daemon: bool = True):
        """
        target(stop_event) should periodically check stop_event.is_set()
        and return when set.
        """
        self._target = target
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._name = name
        self._daemon = daemon

    def start(self):
        if self._thread and self._thread.is_alive():
            return  # already running
        self._stop_event.clear()
        def _run():
            try:
                self._target(self._stop_event)
            finally:
                # make sure the stop flag is set when exiting
                self._stop_event.set()
        self._thread = threading.Thread(target=_run, name=self._name, daemon=self._daemon)
        self._thread.start()

    def stop(self, timeout: Optional[float] = None) -> bool:
        """Request the thread to stop and wait up to timeout seconds."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)
        return not (self._thread and self._thread.is_alive())

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

# # Example target that cooperatively stops
# def my_worker(stop_event: threading.Event):
#     while not stop_event.is_set():
#         # ... do some work ...
#         print("working...")
#         # Use stop_event.wait() to be responsive to stop requests
#         stop_event.wait(0.2)

# if __name__ == "__main__":
#     worker = StoppableThread(target=my_worker, name="my-worker")
#     worker.start()
#     time.sleep(2)       # let it run
#     worker.stop(2.0)    # request stop and wait up to 2s

class toggele_worker:
    def __init__(self, step_fn: Callable[[], None],
                 name: Optional[str] = None, daemon: bool = True, idle_sleep: float = 0.05):
        """
        step_fn() does one unit of work. It should be fast and non-blocking.
        The thread runs step_fn() repeatedly while 'run' is set.
        """
        self._step_fn = step_fn
        self._run = threading.Event()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._name = name
        self._daemon = daemon
        self._idle_sleep = idle_sleep

    def _loop(self):
        try:
            while not self._stop.is_set():
                # Wait until resume() is called, but wake periodically to check for stop
                if not self._run.wait(timeout=0.1):
                    continue
                # Run steps while run is set and not stopping
                while self._run.is_set() and not self._stop.is_set():
                    self._step_fn()
                    # Optional small sleep to avoid busy-looping
                    time.sleep(self._idle_sleep)
        finally:
            self._stop.set()
            self._run.clear()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._run.clear()
        self._thread = threading.Thread(target=self._loop, name=self._name, daemon=self._daemon)
        self._thread.start()

    def resume(self):
        self._run.set()

    def pause(self):
        self._run.clear()

    def stop(self, timeout: Optional[float] = None) -> bool:
        self._run.set()   # wake the thread if it was paused
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=timeout)
        return not (self._thread and self._thread.is_alive())

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def is_working(self) -> bool:
        return self._run.is_set() and self.is_running()

# Example usage
# if __name__ == "__main__":
#     def step():
#         print("tick")

#     w = ToggleWorker(step_fn=step, name="toggle-worker")
#     w.start()
#     w.resume()
#     time.sleep(1.0)
#     w.pause()
#     time.sleep(0.5)
#     w.resume()
#     time.sleep(0.5)
#     w.stop(2.0)