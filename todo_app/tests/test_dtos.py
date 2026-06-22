"""Tests for Data Transfer Objects."""
import pytest
from pydantic import ValidationError

from todo_app.dto.task_create import CreateTaskDTO
from todo_app.dto.task_response import TaskResponseDTO
from todo_app.dto.task_update import UpdateTaskDTO
from todo_app.models.task import Task


class TestCreateTaskDTO:
    """Tests for CreateTaskDTO validation."""

    def test_valid_minimal(self) -> None:
        dto = CreateTaskDTO(title="Hello")
        assert dto.title == "Hello"
        assert dto.description is None
        assert dto.priority == 0

    def test_valid_full(self) -> None:
        dto = CreateTaskDTO(title="Full", description="Desc", priority=3)
        assert dto.title == "Full"
        assert dto.description == "Desc"
        assert dto.priority == 3

    def test_title_empty(self) -> None:
        with pytest.raises(ValidationError):
            CreateTaskDTO(title="")

    def test_title_too_long(self) -> None:
        with pytest.raises(ValidationError):
            CreateTaskDTO(title="A" * 201)

    def test_description_too_long(self) -> None:
        with pytest.raises(ValidationError):
            CreateTaskDTO(title="OK", description="A" * 2001)

    def test_priority_too_low(self) -> None:
        with pytest.raises(ValidationError):
            CreateTaskDTO(title="OK", priority=-1)

    def test_priority_too_high(self) -> None:
        with pytest.raises(ValidationError):
            CreateTaskDTO(title="OK", priority=4)

    def test_priority_default_is_zero(self) -> None:
        dto = CreateTaskDTO(title="No Prio")
        assert dto.priority == 0


class TestUpdateTaskDTO:
    """Tests for UpdateTaskDTO — partial update semantics."""

    def test_task_id_required(self) -> None:
        with pytest.raises(ValidationError):
            UpdateTaskDTO(task_id="")

    def test_all_optional_fields_none_by_default(self) -> None:
        dto = UpdateTaskDTO(task_id="TASK-0001")
        assert dto.task_id == "TASK-0001"
        assert dto.title is None
        assert dto.description is None
        assert dto.priority is None

    def test_partial_title_only(self) -> None:
        dto = UpdateTaskDTO(task_id="TASK-0001", title="New")
        assert dto.title == "New"
        assert dto.description is None
        assert dto.priority is None

    def test_partial_priority_only(self) -> None:
        dto = UpdateTaskDTO(task_id="TASK-0001", priority=2)
        assert dto.title is None
        assert dto.priority == 2

    def test_title_validation_still_applies(self) -> None:
        with pytest.raises(ValidationError):
            UpdateTaskDTO(task_id="TASK-0001", title="")

    def test_priority_validation_still_applies(self) -> None:
        with pytest.raises(ValidationError):
            UpdateTaskDTO(task_id="TASK-0001", priority=5)

    def test_empty_task_id(self) -> None:
        with pytest.raises(ValidationError):
            UpdateTaskDTO(task_id="")


class TestTaskResponseDTO:
    """Tests for TaskResponseDTO and its from_task() factory."""

    def test_from_pending_task(self) -> None:
        task = Task(title="Pending", priority=1)
        task.id = "TASK-0001"

        dto = TaskResponseDTO.from_task(task)

        assert dto.id == "TASK-0001"
        assert dto.title == "Pending"
        assert dto.status == "pending"
        assert dto.priority == 1
        assert dto.is_completed is False
        assert dto.completed_at is None
        assert dto.created_at == task.created_at

    def test_from_completed_task(self) -> None:
        task = Task(title="Done")
        task.id = "TASK-0002"
        task.mark_completed()

        dto = TaskResponseDTO.from_task(task)

        assert dto.status == "completed"
        assert dto.is_completed is True
        assert dto.completed_at is not None

    def test_from_reopened_task(self) -> None:
        task = Task(title="Reopened")
        task.id = "TASK-0003"
        task.mark_completed()
        task.mark_pending()

        dto = TaskResponseDTO.from_task(task)

        assert dto.status == "pending"
        assert dto.is_completed is False
        assert dto.completed_at is None
