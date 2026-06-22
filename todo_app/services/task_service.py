"""Task service — business logic layer."""
from datetime import datetime, timezone

from todo_app.dto.task_create import CreateTaskDTO
from todo_app.dto.task_response import TaskResponseDTO
from todo_app.dto.task_update import UpdateTaskDTO
from todo_app.exceptions import TaskNotFoundError
from todo_app.logger import get_logger
from todo_app.models.task import Task, TaskStatus
from todo_app.repositories.base import TaskRepository

logger = get_logger(__name__)


class TaskService:
    """Business-logic layer for task operations.

    Design principles:
        - Depends on ``TaskRepository`` interface, not concrete storage.
        - Accepts DTOs as input, returns DTOs as output — isolates
          internal models from the command layer.
        - No manual ``validate_*`` methods — Pydantic validates DTOs
          at construction time.
    """

    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def _get_task_or_raise(self, task_id: str) -> Task:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task

    def add_task(self, dto: CreateTaskDTO) -> TaskResponseDTO:
        task = Task(
            title=dto.title,
            description=dto.description,
            priority=dto.priority,
        )
        saved = self.repo.add(task)
        logger.info("Task added — id=%s, title=%r", saved.id, saved.title)
        return TaskResponseDTO.from_task(saved)

    def list_tasks(self, *, include_completed: bool = True) -> list[TaskResponseDTO]:
        tasks = self.repo.get_all()
        if not include_completed:
            tasks = [t for t in tasks if t.status != TaskStatus.COMPLETED]
        logger.debug(
            "Listed %d task(s) (include_completed=%s)", len(tasks), include_completed
        )
        return [TaskResponseDTO.from_task(t) for t in tasks]

    def get_task_detail(self, task_id: str) -> TaskResponseDTO:
        task = self._get_task_or_raise(task_id)
        return TaskResponseDTO.from_task(task)

    def complete_task(self, task_id: str) -> TaskResponseDTO:
        task = self._get_task_or_raise(task_id)
        task.mark_completed()
        self.repo.update(task)
        logger.info("Task %s completed", task_id)
        return TaskResponseDTO.from_task(task)

    def uncomplete_task(self, task_id: str) -> TaskResponseDTO:
        task = self._get_task_or_raise(task_id)
        task.mark_pending()
        self.repo.update(task)
        logger.info("Task %s reopened", task_id)
        return TaskResponseDTO.from_task(task)

    def delete_task(self, task_id: str) -> bool:
        result = self.repo.delete(task_id)
        logger.info("Task %s deleted (existed=%s)", task_id, result)
        return result

    def update_task(self, dto: UpdateTaskDTO) -> TaskResponseDTO:
        task = self._get_task_or_raise(dto.task_id)
        updates = dto.model_dump(exclude_none=True)
        for field, value in updates.items():
            if field != "task_id":
                setattr(task, field, value)
        task.updated_at = datetime.now(timezone.utc).isoformat()
        self.repo.update(task)
        logger.info("Task %s updated — fields=%s", task.id, list(updates.keys()))
        return TaskResponseDTO.from_task(task)
