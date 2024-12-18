import yaml
import os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_FILE = os.path.join(ROOT_DIR, "config.yaml")

def load_config():
    """Load configuration from config.yaml."""
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)

CONFIG = load_config()

# Switch directories if TEST_MODE is set
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

if TEST_MODE:
    CONFIG["directories"]["tasks_dir"] = CONFIG["directories"]["test_tasks_dir"]
    CONFIG["directories"]["archive_dir"] = CONFIG["directories"]["test_archive_dir"]
