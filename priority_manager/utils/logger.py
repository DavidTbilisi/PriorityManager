from datetime import datetime

LOG_FILE = "log.txt"

def log_action(action):
    with open(LOG_FILE, "a") as log:
        log.write(f"{datetime.now().isoformat()} - {action}\n")
