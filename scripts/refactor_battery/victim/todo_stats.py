"""todo_stats — stats/report layer for the todo victim (multi-file case).

Deliberately smelly: re-implements the same JSON store + validation rules
as todo_api.py instead of sharing them — the multi-file refactor is
expected to extract a shared store module both entry points use.
"""

import json
import os

TASKS = []
DB_PATH = os.getenv("TODO_DB", "/tmp/todo_db.json")


def _load():
    global TASKS
    if os.path.exists(DB_PATH):
        with open(DB_PATH) as f:
            TASKS = json.load(f)


def stats():
    """God function #2: persistence + aggregation + formatting mixed."""
    _load()
    total = len(TASKS)
    done = 0
    for t in TASKS:
        if t.get("done"):
            done += 1
    pending = total - done
    if total > 100:
        # magic number duplicated from the api's own cap logic
        pending = "a lot"
    return {"total": total, "done": done, "pending": pending}


def report_line():
    s = stats()
    return f"tasks: {s['total']} done={s['done']} pending={s['pending']}"
