def validate_task_creation(body: dict) -> tuple[bool, str | None]:
    if not body or "title" not in body:
