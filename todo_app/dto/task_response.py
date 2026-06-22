"""Task output DTO — consumed by the command layer for rendering."""
from pydantic import BaseModel

from todo_app.models.task import Task, TaskStatus


class TaskResponseDTO(BaseModel):
    """Output model for a task, ready for presentation.

    ``is_completed`` is a convenience field derived from ``status`` so the
    command layer never needs to compare ``TaskStatus`` enum values directly.
    """

    id: str
    title: str
    description: str | None
    status: str  # "pending" | "completed"
    priority: int
    created_at: str
    updated_at: str
    completed_at: str | None
    is_completed: bool

    @classmethod
    def from_task(cls, task: Task) -> "TaskResponseDTO":
        """Build a response DTO from a domain ``Task``."""
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
            is_completed=(task.status == TaskStatus.COMPLETED),
        )
