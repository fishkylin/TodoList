"""Create-task input DTO with Pydantic validation."""
from pydantic import BaseModel, Field


class CreateTaskDTO(BaseModel):
    """Input model for creating a new task.

    Validation rules (enforced by Pydantic on construction):
        - ``title``: required, 1–200 characters
        - ``description``: optional, max 2000 characters
        - ``priority``: optional, 0–3
    """

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: int = Field(default=0, ge=0, le=3)
