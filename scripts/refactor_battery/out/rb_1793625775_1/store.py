import json
import os
from typing import List, Dict, Any
from models import Task

class TaskStore:
    def __init__(self, db_path: str = "/tmp/todo_db.json"):
        self.db_path = db_path
        self.tasks: List[Task] = []
        self._next_id: int = 1
        self._load()

    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
                    self._next_id = data.get("next_id", 1)
            except Exception as e:
                # In a real app, this should log the error
                pass

    def _dump(self):
        data_to_dump = {
            "tasks": [t.to_dict() for t in self.tasks],
            "next_id": self._next_id
        }
        with open(self.db_path, "w") as f:
            json.dump(data_to_dump, f, indent=4)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.tasks]

    def get_task_by_id(self, task_id: int) -> Task | None:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def create_task(self, title: str, priority: int) -> Task:
        new_task = Task(
            id=self._next_id,
            title=title,
            priority=priority
        )
        self.tasks.append(new_task)
        self._next_id += 1
        self._dump()
        return new_task

    def update_task_done(self, task_id: int, done: bool) -> Task | None:
        for task in self.tasks:
            if task.id == task_id:
                task.done = done
                self._dump()
                return task
        return None

    def delete_task(self, task_id: int) -> bool:
        initial_count = len(
