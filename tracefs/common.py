import threading
from typing import Callable, Optional

stack_trace_path = "/sys/kernel/tracing/stack_trace"
stack_trace_filter_path = "/sys/kernel/tracing/stack_trace_filter"
event_trace_pid = "/sys/kernel/tracing/set_event_pid"

def find_tracing_dir() -> str:
    # Prefer tracefs, fallback to debugfs if older builds
    for d in ("/sys/kernel/tracing", "/sys/kernel/debug/tracing"):
        if os.path.exists(os.path.join(d, "trace_pipe")):
            return d
    raise FileNotFoundError("trace_pipe not found (is tracefs mounted and do you have root?)")


def read_trace_pipe_polling(stop_event: threading.Event,
                    out_path: str,
                    tracing_dir: Optional[str] = None,
                    flush_every: int = 100,
                    poll_timeout_ms: int = 200) -> None:
    """
    Thread target that streams trace_pipe to out_path until stop_event is set.
    Closes resources on exit.
    """
    tracing_dir = tracing_dir or find_tracing_dir()
    pipe_path = os.path.join(tracing_dir, "trace_pipe")

    fd = None
    out_file = None
    try:
        # Open trace_pipe non-blocking so poll/read won't hang shutdown.
        fd = os.open(pipe_path, os.O_RDONLY | os.O_NONBLOCK)
        out_file = open(out_path, "a", encoding="utf-8")

        buf = bytearray()
        n_written = 0

        poller = select.poll()
        poller.register(fd, select.POLLIN | select.POLLHUP | select.POLLERR)

        while not stop_event.is_set():
            events = poller.poll(poll_timeout_ms)
            if not events:
                continue  # timeout: loop again and re-check stop_event

            for _, ev in events:
                if ev & (select.POLLERR | select.POLLHUP):
                    # Pipe error/hangup: exit the loop
                    stop_event.set()
                    break

                if ev & select.POLLIN:
                    try:
                        chunk = os.read(fd, 8192)
                    except BlockingIOError:
                        chunk = b""
                    if not chunk:
                        continue
                    buf.extend(chunk)

                    # Write out complete lines
                    while True:
                        i = buf.find(b"\n")
                        if i < 0:
                            break
                        line = buf[:i+1]
                        del buf[:i+1]
                        out_file.write(line.decode("utf-8", errors="replace"))
                        n_written += 1
                        if flush_every and (n_written % flush_every == 0):
                            out_file.flush()

        # Flush any remaining partial line on stop
        if buf:
            out_file.write(buf.decode("utf-8", errors="replace"))
            out_file.flush()

    finally:
        # Close resources safely
        try:
            if fd is not None:
                os.close(fd)
        except OSError:
            pass
        try:
            if out_file is not None:
                out_file.close()
        except OSError:
            pass


def activate_stack_trace():
    with open(stack_trace_path, "w", encoding="utf-8") as f:
        f.write("1")

def deactivate_stack_trace():
    with open(stack_trace_path, "w", encoding="utf-8") as f:
        f.write("0")

def apply_stack_trace(filter=""):
    with open(stack_trace_filter_path, "w", encoding="utf-8") as f:
        f.write(filter)

def set_event_pid(pid):
    with open(stack_trace_filter_path, "a", encoding="utf-8") as f:
        f.write(str(pid))

def clear_event_pid():
    with open(stack_trace_filter_path, "a", encoding="utf-8") as f:
        f.write("")
    
