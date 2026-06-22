"""Abstract TaskRepository interface."""
from abc import ABC, abstractmethod

from todo_app.models.task import Task


class TaskRepository(ABC):
    """Storage abstraction — the service layer depends only on this interface.

    Using ABC ensures subclasses implement every method; missing one
    raises ``TypeError`` at instantiation time, not later at runtime.
    """

    @abstractmethod
    def get_all(self) -> list[Task]:
        """Return all tasks ordered by creation time (newest first)."""
        ...

    @abstractmethod
    def get_by_id(self, task_id: str) -> Task | None:
        """Return the task with the given ID, or ``None`` if not found."""
        ...

    @abstractmethod
    def add(self, task: Task) -> Task:
        """Persist a new task and return it (with assigned ID)."""
        ...

    @abstractmethod
    def update(self, task: Task) -> Task:
        """Persist changes to an existing task."""
        ...

    @abstractmethod
    def delete(self, task_id: str) -> bool:
        """Remove a task by ID.  Return ``True`` if it existed."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the total number of stored tasks."""
        ...
