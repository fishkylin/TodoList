"""Tests for the JSON-file task repository."""
import json

import pytest

from todo_app.exceptions import TaskNotFoundError
from todo_app.models.task import Task
from todo_app.repositories.json_repo import JsonTaskRepository


class TestJsonRepoEmpty:
    """Behaviour on a fresh (empty) JSON repository."""

    def test_get_all_empty(self, json_repo: JsonTaskRepository) -> None:
        assert json_repo.get_all() == []

    def test_get_by_id_empty(self, json_repo: JsonTaskRepository) -> None:
        assert json_repo.get_by_id("TASK-0001") is None

    def test_count_empty(self, json_repo: JsonTaskRepository) -> None:
        assert json_repo.count() == 0

    def test_delete_nonexistent(self, json_repo: JsonTaskRepository) -> None:
        assert json_repo.delete("TASK-9999") is False

    def test_creates_file_on_first_add(self, json_repo: JsonTaskRepository) -> None:
        assert not json_repo.file_path.exists()
        json_repo.add(Task(title="First"))
        assert json_repo.file_path.exists()


class TestJsonRepoAdd:
    """Tests for adding tasks."""

    def test_add_assigns_id(self, json_repo: JsonTaskRepository) -> None:
        saved = json_repo.add(Task(title="First"))
        assert saved.id == "TASK-0001"

    def test_add_increments_ids(self, json_repo: JsonTaskRepository) -> None:
        t1 = json_repo.add(Task(title="One"))
        t2 = json_repo.add(Task(title="Two"))
        assert t1.id == "TASK-0001"
        assert t2.id == "TASK-0002"

    def test_add_preserves_existing_id(self, json_repo: JsonTaskRepository) -> None:
        task = Task(title="Pre-ID", id="CUSTOM-001")
        saved = json_repo.add(task)
        assert saved.id == "CUSTOM-001"

    def test_add_increases_count(self, json_repo: JsonTaskRepository) -> None:
        assert json_repo.count() == 0
        json_repo.add(Task(title="A"))
        assert json_repo.count() == 1


class TestJsonRepoRetrieve:
    """Tests for retrieving tasks."""

    def test_get_all_newest_first(self, json_repo: JsonTaskRepository) -> None:
        json_repo.add(Task(title="Oldest"))
        t2 = json_repo.add(Task(title="Newest"))

        all_tasks = json_repo.get_all()
        assert len(all_tasks) == 2
        assert all_tasks[0].id == t2.id

    def test_get_by_id_found(self, json_repo: JsonTaskRepository) -> None:
        saved = json_repo.add(Task(title="Find Me"))
        found = json_repo.get_by_id(saved.id)
        assert found is not None
        assert found.title == "Find Me"

    def test_get_by_id_missing(self, json_repo: JsonTaskRepository) -> None:
        json_repo.add(Task(title="Only"))
        assert json_repo.get_by_id("TASK-9999") is None


class TestJsonRepoUpdate:
    """Tests for updating tasks."""

    def test_update_existing(self, json_repo: JsonTaskRepository) -> None:
        saved = json_repo.add(Task(title="Old"))
        saved.title = "New"
        saved.priority = 3
        updated = json_repo.update(saved)

        assert updated.title == "New"
        refetch = json_repo.get_by_id(saved.id)
        assert refetch is not None
        assert refetch.title == "New"

    def test_update_nonexistent_raises(self, json_repo: JsonTaskRepository) -> None:
        ghost = Task(title="Ghost", id="TASK-9999")
        with pytest.raises(TaskNotFoundError) as exc_info:
            json_repo.update(ghost)
        assert exc_info.value.task_id == "TASK-9999"


class TestJsonRepoDelete:
    """Tests for deleting tasks."""

    def test_delete_existing(self, json_repo: JsonTaskRepository) -> None:
        saved = json_repo.add(Task(title="Delete Me"))
        assert json_repo.count() == 1

        result = json_repo.delete(saved.id)
        assert result is True
        assert json_repo.count() == 0

    def test_delete_nonexistent_returns_false(self, json_repo: JsonTaskRepository) -> None:
        json_repo.add(Task(title="Keep"))
        assert json_repo.delete("TASK-9999") is False
        assert json_repo.count() == 1


class TestJsonRepoPersistence:
    """Tests that data survives across repository instances."""

    def test_data_survives_roundtrip(self, json_repo: JsonTaskRepository) -> None:
        """Data written by one instance is readable by another."""
        saved = json_repo.add(Task(title="Persistent"))
        file_path = json_repo.file_path

        # New repo instance pointing to the same file
        repo2 = JsonTaskRepository(file_path)
        tasks = repo2.get_all()
        assert len(tasks) == 1
        assert tasks[0].id == saved.id
        assert tasks[0].title == "Persistent"

    def test_id_counter_persists(self, json_repo: JsonTaskRepository) -> None:
        """The next_index meta counter survives across instances."""
        json_repo.add(Task(title="One"))
        json_repo.add(Task(title="Two"))
        file_path = json_repo.file_path

        repo2 = JsonTaskRepository(file_path)
        t3 = repo2.add(Task(title="Three"))
        assert t3.id == "TASK-0003"


class TestJsonRepoCorruptionRecovery:
    """Tests for the auto-repair behaviour on corrupted data."""

    def test_corrupt_json_resets_to_empty(self, json_repo: JsonTaskRepository) -> None:
        """A file with unparseable content should be reset."""
        json_repo.file_path.write_text("this is not json", encoding="utf-8")

        tasks = json_repo.get_all()
        assert tasks == []
        assert json_repo.count() == 0

    def test_non_dict_root_resets_to_empty(self, json_repo: JsonTaskRepository) -> None:
        """JSON that is a list / string instead of a dict should be reset."""
        json_repo.file_path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")

        tasks = json_repo.get_all()
        assert tasks == []
        assert json_repo.count() == 0

    def test_corruption_repairs_file(self, json_repo: JsonTaskRepository) -> None:
        """After corruption recovery, the file should contain valid data."""
        json_repo.file_path.write_text("garbage", encoding="utf-8")

        # Trigger the repair by reading
        json_repo.get_all()

        # File should now be valid JSON
        data = json.loads(json_repo.file_path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)
        assert "tasks" in data
        assert "meta" in data
        assert data["tasks"] == []

    def test_working_data_is_not_lost(self, json_repo: JsonTaskRepository) -> None:
        """After adding tasks, re-reading should NOT trigger a reset."""
        json_repo.add(Task(title="Keep Me"))
        json_repo.add(Task(title="Me Too"))

        # Reload — should not reset
        tasks = json_repo.get_all()
        assert len(tasks) == 2


class TestJsonRepoFullWorkflow:
    """End-to-end CRUD tests against the JSON repo."""

    def test_full_crud(self, json_repo: JsonTaskRepository) -> None:
        # Add
        task = Task(title="CRUD", description="JSON CRUD", priority=2)
        saved = json_repo.add(task)

        # Read
        assert json_repo.get_by_id(saved.id) is not None
        assert json_repo.count() == 1

        # Update
        saved.title = "Updated CRUD"
        json_repo.update(saved)

        found = json_repo.get_by_id(saved.id)
        assert found is not None
        assert found.title == "Updated CRUD"

        # Delete
        assert json_repo.delete(saved.id) is True
        assert json_repo.count() == 0

    def test_complete_workflow(self, json_repo: JsonTaskRepository) -> None:
        task = json_repo.add(Task(title="To Complete"))
        task.mark_completed()
        json_repo.update(task)

        refetch = json_repo.get_by_id(task.id)
        assert refetch is not None
        assert refetch.status == "completed"
        assert refetch.completed_at is not None

    def test_many_tasks(self, json_repo: JsonTaskRepository) -> None:
        """Stress test: add a moderate number of tasks and verify count."""
        for i in range(50):
            json_repo.add(Task(title=f"Task {i}"))

        assert json_repo.count() == 50
        assert len(json_repo.get_all()) == 50
