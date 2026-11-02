import json
import os
from typing import List, Optional, Dict, Any
from models import Task

class TodoStore:
    def __init__(self, db_path: str = "/tmp/todo_db.json"):
        self.db_path = db_path
        self._tasks: List[Task] = []
        self._next_id: int = 1
        self._load()

    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    data = json.load(f)
                    self._tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
                    self._next_id = data.get("next_id", 1)
            except Exception as e:
                print(f"Error loading database: {e}")
                self._tasks = []
                self._next_id = 1

    def _dump(self):
        data = {
            "tasks": [task.to_dict() for task in self._tasks],
            "next_id": self._next_id
        }
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        return [task.to_dict() for task in self._tasks]

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        for task in self._tasks:
            if task.id == task_id:
                return task.to_dict()
        return None

    def create_task(self, title: str, priority: int) -> Dict[str, Any]:
        new_task = Task(
            id=self._next_id,
            title=title,
            priority=priority
        )
        self._tasks.append(new_task)
        self._next_id += 1
        self._dump()
        return new_task.to_dict()

    def update_task_done(self, task_id: int, done: bool) -> Optional[Dict[str, Any]]:
        for task in self._tasks:
            if task.id == task_id:
                task.done = done
                self._dump()
                return task.to_dict
