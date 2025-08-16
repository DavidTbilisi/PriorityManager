import pytest
import shutil
import os
from priority_manager.utils.config import CONFIG

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
ARCHIVE_DIR = CONFIG["directories"]["archive_dir"]
ORIGINAL_TASKS_DIR = TASKS_DIR
ORIGINAL_ARCHIVE_DIR = ARCHIVE_DIR

@pytest.fixture(autouse=True)
def reset_config_dirs():
    # Ensure CONFIG directory paths restored before each test
    CONFIG['directories']['tasks_dir'] = ORIGINAL_TASKS_DIR
    CONFIG['directories']['archive_dir'] = ORIGINAL_ARCHIVE_DIR
    yield

@pytest.fixture(scope="function")
def setup_dirs():
    """Set up clean tasks and archive directories for each test."""
    for directory in [TASKS_DIR, ARCHIVE_DIR]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)
    yield
    for directory in [TASKS_DIR, ARCHIVE_DIR]:
        if os.path.exists(directory):
            shutil.rmtree(directory)

@pytest.fixture(scope="function")
def sample_task_file():
    """Create a sample task file for testing."""
    sample_file = os.path.join(TASKS_DIR, "sample_task.md")
    if os.path.exists(sample_file):
        print(f"File {sample_file} already exists")
    else:
        print(f"Creating file {sample_file}")
    with open(sample_file, "w") as f:
        f.write(
            "# Sample Task\n\n"
            "**Description:** This is a test task.\n\n"
            "**Priority Score:** 10\n\n"
            "**Due Date:** 2024-12-31\n\n"
            "**Tags:** test, sample\n\n"
            "**Date Added:** 2024-06-01T14:30:00\n\n"
            "**Status:** To Do\n"
        )

        if os.path.exists(sample_file):
            print(f"File {sample_file} created successfully")
    return sample_file