"""Tests for the in-memory task repository."""
import pytest

from todo_app.exceptions import TaskNotFoundError
from todo_app.models.task import Task, TaskStatus
from todo_app.repositories.memory_repo import MemoryTaskRepository


class TestMemoryRepoEmpty:
    """Behaviour on an empty repository."""

    def test_get_all_empty(self, memory_repo: MemoryTaskRepository) -> None:
        assert memory_repo.get_all() == []

    def test_get_by_id_empty(self, memory_repo: MemoryTaskRepository) -> None:
        assert memory_repo.get_by_id("TASK-0001") is None

    def test_count_empty(self, memory_repo: MemoryTaskRepository) -> None:
        assert memory_repo.count() == 0

    def test_delete_nonexistent(self, memory_repo: MemoryTaskRepository) -> None:
        assert memory_repo.delete("TASK-9999") is False


class TestMemoryRepoAdd:
    """Tests for adding tasks."""

    def test_add_assigns_id(self, memory_repo: MemoryTaskRepository) -> None:
        task = Task(title="First")
        saved = memory_repo.add(task)
        assert saved.id == "TASK-0001"

    def test_add_increments_ids(self, memory_repo: MemoryTaskRepository) -> None:
        t1 = memory_repo.add(Task(title="One"))
        t2 = memory_repo.add(Task(title="Two"))
        assert t1.id == "TASK-0001"
        assert t2.id == "TASK-0002"

    def test_add_preserves_existing_id(self, memory_repo: MemoryTaskRepository) -> None:
        task = Task(title="Pre-ID", id="CUSTOM-001")
        saved = memory_repo.add(task)
        assert saved.id == "CUSTOM-001"

    def test_add_increases_count(self, memory_repo: MemoryTaskRepository) -> None:
        assert memory_repo.count() == 0
        memory_repo.add(Task(title="A"))
        assert memory_repo.count() == 1
        memory_repo.add(Task(title="B"))
        assert memory_repo.count() == 2


class TestMemoryRepoRetrieve:
    """Tests for retrieving tasks."""

    def test_get_all_returns_newest_first(self, memory_repo: MemoryTaskRepository) -> None:
        """Tasks should be sorted by created_at descending."""
        t1 = memory_repo.add(Task(title="Oldest"))
        t2 = memory_repo.add(Task(title="Newest"))

        all_tasks = memory_repo.get_all()
        assert len(all_tasks) == 2
        # Newest (t2) should come first
        assert all_tasks[0].id == t2.id
        assert all_tasks[1].id == t1.id

    def test_get_by_id_found(self, memory_repo: MemoryTaskRepository) -> None:
        saved = memory_repo.add(Task(title="Find Me"))
        found = memory_repo.get_by_id(saved.id)
        assert found is not None
        assert found.id == saved.id
        assert found.title == "Find Me"

    def test_get_by_id_missing(self, memory_repo: MemoryTaskRepository) -> None:
        memory_repo.add(Task(title="Only"))
        assert memory_repo.get_by_id("TASK-9999") is None


class TestMemoryRepoUpdate:
    """Tests for updating tasks."""

    def test_update_existing(self, memory_repo: MemoryTaskRepository) -> None:
        saved = memory_repo.add(Task(title="Old Title"))
        saved.title = "New Title"
        saved.priority = 3
        updated = memory_repo.update(saved)

        assert updated.title == "New Title"
        assert updated.priority == 3

        # Verify persistence
        refetch = memory_repo.get_by_id(saved.id)
        assert refetch is not None
        assert refetch.title == "New Title"

    def test_update_nonexistent_raises(self, memory_repo: MemoryTaskRepository) -> None:
        ghost = Task(title="Ghost", id="TASK-9999")
        with pytest.raises(TaskNotFoundError) as exc_info:
            memory_repo.update(ghost)
        assert exc_info.value.task_id == "TASK-9999"


class TestMemoryRepoDelete:
    """Tests for deleting tasks."""

    def test_delete_existing(self, memory_repo: MemoryTaskRepository) -> None:
        saved = memory_repo.add(Task(title="Delete Me"))
        assert memory_repo.count() == 1

        result = memory_repo.delete(saved.id)
        assert result is True
        assert memory_repo.count() == 0
        assert memory_repo.get_by_id(saved.id) is None

    def test_delete_nonexistent_returns_false(self, memory_repo: MemoryTaskRepository) -> None:
        memory_repo.add(Task(title="Keep"))
        assert memory_repo.count() == 1
        assert memory_repo.delete("TASK-9999") is False
        assert memory_repo.count() == 1


class TestMemoryRepoIntegration:
    """End-to-end workflow tests."""

    def test_full_crud_workflow(self, memory_repo: MemoryTaskRepository) -> None:
        # Add
        task = Task(title="CRUD", description="Test", priority=1)
        saved = memory_repo.add(task)

        # Read
        assert memory_repo.get_by_id(saved.id) is not None
        assert memory_repo.count() == 1

        # Update
        saved.title = "Updated"
        memory_repo.update(saved)

        # Verify
        found = memory_repo.get_by_id(saved.id)
        assert found is not None
        assert found.title == "Updated"

        # Delete
        assert memory_repo.delete(saved.id) is True
        assert memory_repo.count() == 0

    def test_complete_workflow(self, memory_repo: MemoryTaskRepository) -> None:
        task = memory_repo.add(Task(title="To Complete"))
        task.mark_completed()
        memory_repo.update(task)

        refetch = memory_repo.get_by_id(task.id)
        assert refetch is not None
        assert refetch.status == TaskStatus.COMPLETED
        assert refetch.completed_at is not None
