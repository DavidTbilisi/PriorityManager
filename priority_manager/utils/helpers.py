import os
from ..utils.config import CONFIG
import click

TASKS_DIR = CONFIG["directories"]["tasks_dir"]
ARCHIVE_DIR = CONFIG["directories"]["archive_dir"]

def ensure_dirs():
    if not os.path.exists(TASKS_DIR):
        os.makedirs(TASKS_DIR)
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

def calculate_priority():
    urgency = click.prompt("Enter urgency (1-5, 5 = most urgent)", type=int, default=3)
    importance = click.prompt("Enter importance (1-5, 5 = most important)", type=int, default=3)
    effort = click.prompt("Enter effort (1-5, 5 = most effort required)", type=int, default=3)
    return urgency * 2 + importance * 3 - effort
