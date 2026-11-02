import json
import os
from typing import List, Dict, Any
from models import Task

class TaskStore:
    def __init__(self, db_path: str = "/tmp/todo_db.json"):
        self.db_path = db_path
        self._tasks: List[Task] = []
        self._next_id: int = 1

    def _load_data(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    data = json.load(f)
                    # Assuming the loaded data structure matches the old TASKS list
                    # We need to reconstruct Task objects from the loaded dicts
                    self._tasks = [Task.from_dict(item) for item in data]
                    # Determine the next ID based on loaded data
                    if self._tasks:
                        self._next_id = max(t.id for t in self._tasks) + 1
                    else:
                        self._next_id = 1
            except Exception as e:
                print(f"Error loading database: {e}")
                self._tasks = []
                self._next_id = 1

    def _dump_data(self):
        # Convert Task objects back to serializable dicts for saving
        serializable_tasks = [task.to_dict() for task in self._tasks]
        with open(self.db_path, "w") as f:
            json.dump(serializable_tasks, f, indent=4)

    def load(self):
        self._load_data()

    def save(self):
        self._dump_data()

    def get_all_tasks(self) -> List[Task]:
        return self._tasks

    def get_task_by_id(self, task_id: int) -> Task | None:
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def add_task(self, title: str, priority: int) -> Task:
        new_task = Task(
            id=self._next_id,
            title=title,
            done=False,
            priority=priority
        )
        self._tasks.append(new_task)
        self._next_id += 1
        return new_task

    def update_task_done(self, task_id: int, done: bool
