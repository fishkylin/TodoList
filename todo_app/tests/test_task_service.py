"""Tests for the TaskService business-logic layer."""
import pytest

from todo_app.dto.task_create import CreateTaskDTO
from todo_app.dto.task_update import UpdateTaskDTO
from todo_app.exceptions import TaskNotFoundError
from todo_app.models.task import Task
from todo_app.repositories.memory_repo import MemoryTaskRepository
from todo_app.services.task_service import TaskService

# We test through the service + in-memory repo (integration style).
# This is intentional — the service IS the unit under test, and
# MemoryTaskRepository is a lightweight, deterministic collaborator.


class TestServiceAddTask:
    """Tests for add_task()."""

    def test_add_returns_response_dto(self, task_service: TaskService) -> None:
        dto = CreateTaskDTO(title="Hello")
        result = task_service.add_task(dto)

        assert result.title == "Hello"
        assert result.id.startswith("TASK-")
        assert result.is_completed is False
        assert result.description is None

    def test_add_with_description(self, task_service: TaskService) -> None:
        dto = CreateTaskDTO(title="Title", description="Details")
        result = task_service.add_task(dto)
        assert result.description == "Details"

    def test_add_with_priority(self, task_service: TaskService) -> None:
        dto = CreateTaskDTO(title="Urgent", priority=3)
        result = task_service.add_task(dto)
        assert result.priority == 3

    def test_add_multiple_increments_ids(
        self, task_service: TaskService
    ) -> None:
        r1 = task_service.add_task(CreateTaskDTO(title="One"))
        r2 = task_service.add_task(CreateTaskDTO(title="Two"))
        assert r1.id != r2.id


class TestServiceListTasks:
    """Tests for list_tasks()."""

    def test_list_empty(self, task_service: TaskService) -> None:
        assert task_service.list_tasks() == []

    def test_list_includes_completed_by_default(
        self, task_service: TaskService, memory_repo: MemoryTaskRepository
    ) -> None:
        memory_repo.add(Task(title="Pending"))
        done = memory_repo.add(Task(title="Done"))
        done.mark_completed()
        memory_repo.update(done)

        results = task_service.list_tasks()
        assert len(results) == 2

    def test_list_exclude_completed(
        self, task_service: TaskService, memory_repo: MemoryTaskRepository
    ) -> None:
        pending = memory_repo.add(Task(title="Keep"))
        done = memory_repo.add(Task(title="Hide"))
        done.mark_completed()
        memory_repo.update(done)

        results = task_service.list_tasks(include_completed=False)
        assert len(results) == 1
        assert results[0].id == pending.id

    def test_list_all_completed_returns_empty_when_excluded(
        self, task_service: TaskService, memory_repo: MemoryTaskRepository
    ) -> None:
        done = memory_repo.add(Task(title="Done"))
        done.mark_completed()
        memory_repo.update(done)

        results = task_service.list_tasks(include_completed=False)
        assert results == []


class TestServiceGetTaskDetail:
    """Tests for get_task_detail()."""

    def test_existing_task(self, task_service: TaskService) -> None:
        added = task_service.add_task(CreateTaskDTO(title="Detail"))
        detail = task_service.get_task_detail(added.id)

        assert detail.id == added.id
        assert detail.title == "Detail"

    def test_nonexistent_task_raises(self, task_service: TaskService) -> None:
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_service.get_task_detail("TASK-9999")
        assert exc_info.value.task_id == "TASK-9999"


class TestServiceCompleteAndUncomplete:
    """Tests for complete_task() and uncomplete_task()."""

    def test_complete_task(self, task_service: TaskService) -> None:
        added = task_service.add_task(CreateTaskDTO(title="To Do"))
        result = task_service.complete_task(added.id)

        assert result.is_completed is True
        assert result.status == "completed"
        assert result.completed_at is not None

    def test_complete_nonexistent_raises(self, task_service: TaskService) -> None:
        with pytest.raises(TaskNotFoundError):
            task_service.complete_task("TASK-9999")

    def test_uncomplete_task(self, task_service: TaskService) -> None:
        added = task_service.add_task(CreateTaskDTO(title="Done"))
        task_service.complete_task(added.id)

        reopened = task_service.uncomplete_task(added.id)
        assert reopened.is_completed is False
        assert reopened.status == "pending"
        assert reopened.completed_at is None

    def test_uncomplete_nonexistent_raises(self, task_service: TaskService) -> None:
        with pytest.raises(TaskNotFoundError):
            task_service.uncomplete_task("TASK-9999")

    def test_toggle_cycle(self, task_service: TaskService) -> None:
        """Complete → uncomplete → complete should be idempotent in outcome."""
        added = task_service.add_task(CreateTaskDTO(title="Toggle"))

        c1 = task_service.complete_task(added.id)
        assert c1.is_completed

        u1 = task_service.uncomplete_task(added.id)
        assert not u1.is_completed

        c2 = task_service.complete_task(added.id)
        assert c2.is_completed


class TestServiceDeleteTask:
    """Tests for delete_task()."""

    def test_delete_existing(self, task_service: TaskService) -> None:
        added = task_service.add_task(CreateTaskDTO(title="Gone"))
        result = task_service.delete_task(added.id)

        assert result is True
        with pytest.raises(TaskNotFoundError):
            task_service.get_task_detail(added.id)

    def test_delete_nonexistent(self, task_service: TaskService) -> None:
        assert task_service.delete_task("TASK-9999") is False


class TestServiceUpdateTask:
    """Tests for update_task()."""

    def test_update_title_only(self, task_service: TaskService) -> None:
        added = task_service.add_task(CreateTaskDTO(title="Old"))
        dto = UpdateTaskDTO(task_id=added.id, title="New Title")
        result = task_service.update_task(dto)

        assert result.title == "New Title"
        # Other fields unchanged
        assert result.priority == 0

    def test_update_priority_only(self, task_service: TaskService) -> None:
        added = task_service.add_task(CreateTaskDTO(title="Prio", priority=0))
        dto = UpdateTaskDTO(task_id=added.id, priority=3)
        result = task_service.update_task(dto)

        assert result.priority == 3
        assert result.title == "Prio"

    def test_update_description_to_none_not_sent(
        self, task_service: TaskService
    ) -> None:
        """Passing None via exclude_none means the field is not set —
        we must explicitly pass a description to verify it sticks."""
        added = task_service.add_task(
            CreateTaskDTO(title="Desc", description="Original")
        )
        # Only pass task_id — nothing should change
        dto = UpdateTaskDTO(task_id=added.id, title="New Title")
        result = task_service.update_task(dto)

        assert result.title == "New Title"
        assert result.description == "Original"

    def test_update_nonexistent_raises(self, task_service: TaskService) -> None:
        dto = UpdateTaskDTO(task_id="TASK-9999", title="Ghost")
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_service.update_task(dto)
        assert exc_info.value.task_id == "TASK-9999"


class TestServiceIntegration:
    """Higher-level orchestration tests."""

    def test_sequential_workflow(self, task_service: TaskService) -> None:
        """Simulate a real user session."""
        # User creates three tasks
        t1 = task_service.add_task(CreateTaskDTO(title="Buy milk"))
        t2 = task_service.add_task(CreateTaskDTO(title="Pay bills", priority=2))
        t3 = task_service.add_task(CreateTaskDTO(title="Read book"))

        # List should show all three
        assert len(task_service.list_tasks()) == 3

        # User completes one
        task_service.complete_task(t2.id)

        # Filter out completed
        pending = task_service.list_tasks(include_completed=False)
        assert len(pending) == 2
        pending_ids = {t.id for t in pending}
        assert t1.id in pending_ids
        assert t3.id in pending_ids

        # User edits another
        task_service.update_task(UpdateTaskDTO(task_id=t1.id, title="Buy milk + eggs"))

        # User deletes the third
        task_service.delete_task(t3.id)

        # Final state
        all_tasks = task_service.list_tasks()
        assert len(all_tasks) == 2


class TestServiceNumericShorthand:
    """All task_id-accepting service methods must handle numeric shorthand.

    Each test adds a task (which gets ``TASK-0001``), then accesses it
    via the shorthand ``"1"``.
    """

    def test_get_task_detail(self, task_service: TaskService) -> None:
        added = task_service.add_task(CreateTaskDTO(title="Detail"))
        detail = task_service.get_task_detail("1")
        assert detail.id == added.id

    def test_complete_task(self, task_service: TaskService) -> None:
        task_service.add_task(CreateTaskDTO(title="To Complete"))
        result = task_service.complete_task("1")
        assert result.is_completed is True

    def test_uncomplete_task(self, task_service: TaskService) -> None:
        task_service.add_task(CreateTaskDTO(title="Toggle"))
        task_service.complete_task("1")
        result = task_service.uncomplete_task("1")
        assert result.is_completed is False

    def test_update_task(self, task_service: TaskService) -> None:
        task_service.add_task(CreateTaskDTO(title="Old"))
        dto = UpdateTaskDTO(task_id="1", title="New Title")
        result = task_service.update_task(dto)
        assert result.title == "New Title"

    def test_delete_task(self, task_service: TaskService) -> None:
        task_service.add_task(CreateTaskDTO(title="Delete Me"))
        assert task_service.delete_task("1") is True

    def test_nonexistent_shorthand_raises(self, task_service: TaskService) -> None:
        """Shorthand for a non-existent index raises ``TaskNotFoundError``."""
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_service.get_task_detail("9999")
        assert "TASK-9999" in str(exc_info.value)

    def test_full_format_still_works(self, task_service: TaskService) -> None:
        """Existing callers using full ``TASK-XXXX`` format are not broken."""
        added = task_service.add_task(CreateTaskDTO(title="Full Format"))
        detail = task_service.get_task_detail(added.id)
        assert detail.id == added.id
