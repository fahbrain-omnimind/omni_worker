class Task:
    def __init__(self, id: int, title: str, done: bool = False, created: int = None, priority: int = 3):
        self.id = id
        self.title = title
        self.done = done
        self.created = created if created is not None else int(time.time())
        self.priority = priority

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "created": self.created,
            "priority": self.priority
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            title=data['title'],
            done=data.get('done', False),
            created=data.get('created'),
            priority=data.get('priority', 3)
        )
