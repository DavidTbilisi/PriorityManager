from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import ClassVar, Dict, Optional


@dataclass
class TaskFile:
    """Single source of truth for reading and writing task markdown files.

    Preserves all known fields on round-trip and keeps unknown fields verbatim
    so future schema additions don't silently drop data.
    """

    _KNOWN: ClassVar[Dict[str, str]] = {
        "Name": "name",
        "List": "list_name",
        "Description": "description",
        "Priority Score": "priority_score",
        "Due Date": "due_date",
        "Tags": "tags",
        "Date Added": "date_added",
        "Date Edited": "date_edited",
        "Status": "status",
    }

    name: str = ""
    list_name: str = ""
    description: str = "No description"
    priority_score: int = 0
    due_date: str = "No due date"
    tags: str = ""
    date_added: str = ""
    date_edited: str = ""
    status: str = "To Do"
    filepath: str = ""
    _extra: dict = field(default_factory=dict, repr=False, compare=False)

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------

    @classmethod
    def read(cls, filepath: str) -> "TaskFile":
        """Parse a task markdown file and return a populated TaskFile."""
        obj = cls(filepath=filepath)
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.startswith("**"):
                    continue
                m = re.match(r"\*\*([^*]+):\*\*\s*(.*)", line.strip())
                if not m:
                    continue
                key, val = m.group(1).strip(), m.group(2).strip()
                attr = cls._KNOWN.get(key)
                if attr == "priority_score":
                    try:
                        obj.priority_score = int(val)
                    except ValueError:
                        pass
                elif attr:
                    setattr(obj, attr, val)
                else:
                    obj._extra[key] = val
        # Fall back to filename stem when Name field is absent
        if not obj.name:
            obj.name = os.path.splitext(os.path.basename(filepath))[0]
        return obj

    def write(self, filepath: Optional[str] = None) -> None:
        """Write this task to disk, preserving all fields."""
        path = filepath or self.filepath
        if not path:
            raise ValueError("No filepath specified for TaskFile.write()")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"**Name:** {self.name}\n\n")
            if self.list_name:
                f.write(f"**List:** {self.list_name}\n\n")
            f.write(f"**Description:** {self.description}\n\n")
            f.write(f"**Priority Score:** {self.priority_score}\n\n")
            f.write(f"**Due Date:** {self.due_date}\n\n")
            f.write(f"**Tags:** {self.tags}\n\n")
            if self.date_added:
                f.write(f"**Date Added:** {self.date_added}\n\n")
            if self.date_edited:
                f.write(f"**Date Edited:** {self.date_edited}\n\n")
            for key, val in self._extra.items():
                f.write(f"**{key}:** {val}\n\n")
            f.write(f"**Status:** {self.status}\n")

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a plain dict compatible with the legacy get_task_details format."""
        file_name = os.path.splitext(os.path.basename(self.filepath))[0] if self.filepath else self.name
        date_added = self.date_added
        match = re.search(r"\d{4}-\d{2}-\d{2}", file_name)
        if match:
            start_date = match.group()
        elif date_added and len(date_added) >= 10:
            start_date = date_added[:10]
        else:
            start_date = "N/A"
        return {
            "Task Name": self.name,
            "Priority Score": self.priority_score,
            "File Name": file_name,
            "Filepath": self.filepath,
            "Start Date": start_date,
            "Due Date": self.due_date,
            "Status": self.status,
            "Description": self.description,
            "Tags": self.tags,
            "Date Added": date_added,
            "List": self.list_name,
        }
