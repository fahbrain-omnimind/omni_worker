"""Smoke contract for todo_api — the refactor must keep ALL of this passing."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ["TODO_DB"] = "/tmp/todo_db_battery.json"

import importlib
import todo_api


def _reset():
    todo_api.TASKS.clear()
    todo_api._NEXT_ID[0] = 1
    if os.path.exists(os.environ["TODO_DB"]):
        os.remove(os.environ["TODO_DB"])


def test_create_and_list():
    _reset()
    code, task = todo_api.handle_request("POST", "/tasks", {"title": "buy milk"})
    assert code == 201 and task["id"] == 1 and task["done"] is False and task["priority"] == 3
    code, tasks = todo_api.handle_request("GET", "/tasks")
    assert code == 200 and len(tasks) == 1


def test_validation():
    _reset()
    code, _ = todo_api.handle_request("POST", "/tasks", {})
    assert code == 400
    code, _ = todo_api.handle_request("POST", "/tasks", {"title": "x" * 141})
    assert code == 400


def test_get_done_delete():
    _reset()
    _, task = todo_api.handle_request("POST", "/tasks", {"title": "a", "priority": 1})
    code, got = todo_api.handle_request("GET", f"/tasks/{task['id']}")
    assert code == 200 and got["title"] == "a"
    code, done = todo_api.handle_request("POST", f"/tasks/{task['id']}/done")
    assert code == 200 and done["done"] is True
    code, _ = todo_api.handle_request("DELETE", f"/tasks/{task['id']}")
    assert code == 200
    code, _ = todo_api.handle_request("GET", f"/tasks/{task['id']}")
    assert code == 404


def test_404s():
    _reset()
    code, _ = todo_api.handle_request("GET", "/tasks/99")
    assert code == 404
    code, _ = todo_api.handle_request("DELETE", "/tasks/99")
    assert code == 404
    code, _ = todo_api.handle_request("PUT", "/nope")
    assert code == 404
