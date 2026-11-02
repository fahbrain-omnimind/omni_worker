import json
import os
from typing import List, Optional, Dict, Any
from models import Task

class TaskStore:
    def __init__(self, db_path: str = os.getenv("TODO_DB", "/tmp/todo_db.json")):
        self.db_path = db_path
        self._tasks: List[Task] = []
        self._next_id: int = 1

    def _load_tasks(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    data = json.load(f)
                    self._tasks = [Task.from_dict(item) for item in data.get("tasks", [])]
                    self._next_id = data.get("next_id", 1)
            except Exception as e:
                print(f"Error loading database: {e}")
                self._tasks = []
                self._next_id = 1

    def _dump_tasks(self):
        data = {
            "tasks": [task.to_dict() for task in self._tasks],
            "next_id": self._next_id
        }
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=4)

    def load(self):
        self._load_tasks()

    def save(self):
        self._dump_tasks()

    def get_all_tasks(self) -> List[Task]:
        return self._tasks

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def create_task(self, title: str, priority: int) -> Task:
        new_task = Task(
            id=self._next_id,
            title=title,
            priority=priority
        )
        self._tasks.append(new_task)
        self._next_id += 1
        return new_task

    def update_task_done(self, task_id: int, done: bool) -> Optional[Task]:
        for task in self._tasks:
            if task.id == task_id:
                task.done = done
                return task
        return None

    def delete_task(self, task_
