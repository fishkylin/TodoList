"""Custom exception hierarchy.

Catch ``TodoError`` to handle any application-level error generically.
"""
class TodoError(Exception):
    """Base class for all application exceptions."""


class StorageError(TodoError):
    """Raised on JSON read / write failures (corruption, disk full, etc.)."""


class TaskNotFoundError(TodoError):
    """Raised when a task lookup by ID fails — carries the task_id for logging."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task '{task_id}' not found")
