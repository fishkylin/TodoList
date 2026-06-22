"""Task domain model, status enum, and ID generator."""
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task lifecycle states."""
    PENDING = "pending"
    COMPLETED = "completed"


class Task(BaseModel):
    """Core task entity.

    Attributes:
        id: Unique identifier assigned by the repository on first save.
            Defaults to ``""`` (not yet persisted).
        title: Required, 1–200 characters.
        description: Optional, up to 2000 characters.
        status: ``TaskStatus.PENDING`` or ``TaskStatus.COMPLETED``.
        priority: 0–3 (0 = lowest, 3 = highest).
        created_at: ISO‑8601 UTC timestamp, set automatically.
        updated_at: ISO‑8601 UTC timestamp, updated on every mutation.
        completed_at: ISO‑8601 UTC timestamp, set when status becomes COMPLETED.
    """

    id: str = Field(default="", description="Assigned by repository on first persist")
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: str = Field(default=TaskStatus.PENDING)
    priority: int = Field(default=0, ge=0, le=3)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )
    completed_at: str | None = Field(default=None)

    def mark_completed(self) -> None:
        """Transition the task to COMPLETED and stamp timestamps."""
        now = datetime.now(timezone.utc).isoformat()
        self.status = TaskStatus.COMPLETED
        self.updated_at = now
        self.completed_at = now

    def mark_pending(self) -> None:
        """Transition the task back to PENDING and clear completed_at."""
        self.status = TaskStatus.PENDING
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self.completed_at = None


def generate_task_id(index: int) -> str:
    """Generate a zero-padded task ID, e.g. ``TASK-0042``."""
    return f"TASK-{index:04d}"
