import os
import shlex
import subprocess
import threading



def _pump(pipe, path):
    with open(path, "a", encoding="utf-8") as f:
        for line in iter(pipe.readline, ''):
            f.write(line)
    pipe.close()

def run_process(cmd, stdout_path=None, stderr_path=None):
    base_dir = os.getcwd()

    if stdout_path == None:
        stdout_path = base_dir + "/stdout.log"

    if stderr_path == None:
        stderr_path = base_dir + "/stderr.log"
    
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        t_out = threading.Thread(target=_pump, args=(proc.stdout, stdout_path), daemon=True)
        t_err = threading.Thread(target=_pump, args=(proc.stderr, stderr_path), daemon=True)
        t_out.start()
        t_err.start()

        return proc, t_out, t_err

    except Exception:
        print("failed to create process..!!!")
        return None

    return None    



def stop_process(proc, reader_threads=None, timeout=5.0, kill_children=True):
    """
    Gracefully stop a subprocess that has background threads reading its stdout/stderr.
    - Ask the process to terminate softly
    - Close our pipe ends so reader threads see EOF and exit
    - Join reader threads
    - Escalate to kill if the process doesn't exit in time

    reader_threads: iterable of Thread objects (e.g., [t_out, t_err]) or None
    Returns the final returncode.
    """
    # 1) Soft stop
    try:
        if os.name == "nt":
            try:
                proc.send_signal(signal.CTRL_BREAK_EVENT)
            except Exception:
                proc.terminate()
        else:
            if kill_children:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                except Exception:
                    proc.terminate()
            else:
                proc.terminate()
    except Exception:
        pass

    # 2) Close our pipe ends so the reader threads exit cleanly
    for pipe in (getattr(proc, "stdout", None), getattr(proc, "stderr", None)):
        try:
            if pipe:
                pipe.close()
        except Exception:
            pass

    # 3) Wait for graceful exit
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        # 4) Escalate
        try:
            if os.name == "nt":
                proc.kill()
            else:
                if kill_children:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except Exception:
                        proc.kill()
                else:
                    proc.kill()
        except Exception:
            pass
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            pass

    # 5) Join reader threads
    if reader_threads:
        for t in reader_threads:
            try:
                if t and t.is_alive():
                    t.join(timeout=timeout)
            except Exception:
                pass

    return proc.returncode
