#!/usr/bin/env python3
import sys
import time
import subprocess
from workers import *
from helpers.runner import *
import tracefs.common as tfs_common
import tracefs.events.kmem

def print_usage():
    print("Usage: python prof.py <command> [args...]")
    sys.exit(2)

def main():    
    if len(sys.argv) < 2:
        print_usage()

    cmd = sys.argv[1:]
    if len(cmd) == 1:
        cmd = shlex.split(cmd[0])
    proc, t_out, t_err = run_process(cmd)
    
    tfs_common.set_event_pid(proc.pid)
    activate_kmem_kmalloc()
    activate_kmem_kfree()
    activate_kmem_cache_alloc()
    activate_kmem_cache_free()
    
    out = os.getcwd() + "/trace.log"
    trace_thread = stoppable_worker(target=lambda stop_event: read_trace_pipe_polling(stop_event, out_path=out), name="trace-reader")
    trace_thread.start()

    proc, t_out, t_err = run_process(cmd)
    proc.wait()

    deactivate_kmem_cache_alloc()
    deactivate_kmem_cache_free()
    deactivate_kmem_kmalloc()
    deactivate_kmem_kfree()
    tfs_common.clear_event_pid()
    stop_process(proc, reader_threads=[t_out, t_err])
    trace_thread.stop()


if __name__ == "__main__":
    main()