from datetime import datetime

def write_control_string(path: str, ctrl_str: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    msg = f"Control write : {timestamp}\n\tpath : {path}\n\tstring : {ctrl_str}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(ctrl_str)
        print(msg)