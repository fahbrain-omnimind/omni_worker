"""todo_api — tiny task API (VICTIM app for the refactor battery).

Deliberately smelly but behavior-complete: god function, global mutable
state, duplicated validation, magic numbers, mixed concerns. The smoke
tests in test_todo_api.py define the contract a refactor must preserve.
"""

import json
import os
import time

TASKS = []
_NEXT_ID = [1]
DB_PATH = os.getenv("TODO_DB", "/tmp/todo_db.json")


def _dump():
    with open(DB_PATH, "w") as f:
        json.dump(TASKS, f)


def _load():
    global TASKS
    if os.path.exists(DB_PATH):
        with open(DB_PATH) as f:
            TASKS = json.load(f)


def handle_request(method, path, body=None):
    """God function: routing + validation + persistence + formatting."""
    _load()
    if method == "GET" and path == "/tasks":
        return 200, TASKS
    if method == "GET" and path.startswith("/tasks/"):
        tid = int(path.split("/")[-1])
        found = None
        for t in TASKS:
            if t["id"] == tid:
                found = t
        if found is None:
            return 404, {"error": "not found"}
        return 200, found
    if method == "POST" and path == "/tasks":
        if not body or "title" not in body:
            return 400, {"error": "title required"}
        if len(body["title"]) > 140:
            return 400, {"error": "title too long"}
        task = {
            "id": _NEXT_ID[0],
            "title": body["title"],
            "done": False,
            "created": int(time.time()),
            "priority": body.get("priority", 3),
        }
        _NEXT_ID[0] += 1
        TASKS.append(task)
        _dump()
        return 201, task
    if method == "POST" and path.startswith("/tasks/") and path.endswith("/done"):
        tid = int(path.split("/")[2])
        for t in TASKS:
            if t["id"] == tid:
                t["done"] = True
                _dump()
                return 200, t
        return 404, {"error": "not found"}
    if method == "DELETE" and path.startswith("/tasks/"):
        tid = int(path.split("/")[-1])
        for i, t in enumerate(TASKS):
            if t["id"] == tid:
                TASKS.pop(i)
                _dump()
                return 200, {"deleted": tid}
        return 404, {"error": "not found"}
    return 404, {"error": "not found"}
