"""Update-task input DTO — partial update with Pydantic validation."""
from pydantic import BaseModel, Field


class UpdateTaskDTO(BaseModel):
    """Input model for updating an existing task.

    All optional fields default to ``None``, meaning "do not modify".
    Only explicitly provided fields are applied.
    """

    task_id: str = Field(..., min_length=1)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: int | None = Field(default=None, ge=0, le=3)
