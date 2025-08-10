from datetime import datetime

LOG_FILE = "log.txt"

def log_action(action):
    # Ensure UTF-8 to support non-ASCII task names
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{datetime.now().isoformat()} - {action}\n")
