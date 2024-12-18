import yaml
import os
import importlib.resources

def load_config():
    """Load configuration from config.yaml."""
    with importlib.resources.open_text("priority_manager", "config.yaml") as f:
        return yaml.safe_load(f)

# Load the configuration
CONFIG = load_config()

# Switch directories if TEST_MODE is set
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

if TEST_MODE:
    CONFIG["directories"]["tasks_dir"] = CONFIG["directories"]["test_tasks_dir"]
    CONFIG["directories"]["archive_dir"] = CONFIG["directories"]["test_archive_dir"]
