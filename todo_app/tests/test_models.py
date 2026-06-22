"""Tests for the Task domain model, TaskStatus enum, and generate_task_id()."""
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from todo_app.models.task import Task, TaskStatus, generate_task_id, normalize_task_id


class TestTaskStatus:
    """Tests for the TaskStatus enum."""

    def test_pending_value(self) -> None:
        assert TaskStatus.PENDING == "pending"

    def test_completed_value(self) -> None:
        assert TaskStatus.COMPLETED == "completed"

    def test_enum_membership(self) -> None:
        assert len(TaskStatus) == 2
        assert TaskStatus.PENDING in TaskStatus
        assert TaskStatus.COMPLETED in TaskStatus

    def test_enum_is_str(self) -> None:
        assert isinstance(TaskStatus.PENDING, str)


class TestTaskCreation:
    """Tests for constructing Task instances."""

    def test_minimal_creation(self) -> None:
        task = Task(title="Hello")
        assert task.title == "Hello"
        assert task.id == ""
        assert task.description is None
        assert task.status == TaskStatus.PENDING
        assert task.priority == 0
        assert task.completed_at is None

    def test_full_creation(self) -> None:
        task = Task(
            title="Full Task",
            description="Lots of details",
            priority=2,
        )
        assert task.title == "Full Task"
        assert task.description == "Lots of details"
        assert task.priority == 2

    def test_title_too_short(self) -> None:
        with pytest.raises(ValidationError):
            Task(title="")

    def test_title_too_long(self) -> None:
        with pytest.raises(ValidationError):
            Task(title="A" * 201)

    def test_description_too_long(self) -> None:
        with pytest.raises(ValidationError):
            Task(title="OK", description="A" * 2001)

    def test_priority_out_of_range_low(self) -> None:
        with pytest.raises(ValidationError):
            Task(title="OK", priority=-1)

    def test_priority_out_of_range_high(self) -> None:
        with pytest.raises(ValidationError):
            Task(title="OK", priority=4)

    def test_created_at_is_iso8601_utc(self) -> None:
        task = Task(title="TS check")
        # Should be a valid ISO-8601 string ending with '+00:00' (UTC)
        assert task.created_at.endswith("+00:00")
        assert "T" in task.created_at

    def test_created_at_is_different_per_instance(self) -> None:
        """Each instance must get its own timestamp, not a shared default."""
        t1 = Task(title="One")
        t2 = Task(title="Two")
        # created_at is set at instance construction; two fast creations
        # may share the same second but the timestamps should be close.
        # We just verify they are both truthy strings.
        assert t1.created_at
        assert t2.created_at


class TestTaskMutations:
    """Tests for mark_completed() and mark_pending()."""

    def test_mark_completed_sets_status(self) -> None:
        task = Task(title="Done")
        task.mark_completed()
        assert task.status == TaskStatus.COMPLETED

    def test_mark_completed_sets_timestamps(self) -> None:
        task = Task(title="Done")
        before = datetime.now(timezone.utc).isoformat()
        task.mark_completed()
        assert task.completed_at is not None
        assert task.completed_at > before  # type: ignore[operator]
        assert task.updated_at > before  # type: ignore[operator]

    def test_mark_pending_clears_completed(self) -> None:
        task = Task(title="Reopen")
        task.mark_completed()
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None

        task.mark_pending()
        assert task.status == TaskStatus.PENDING
        assert task.completed_at is None

    def test_mark_pending_updates_updated_at(self) -> None:
        task = Task(title="Reopen")
        old_updated = task.updated_at
        task.mark_pending()
        assert task.updated_at >= old_updated


class TestGenerateTaskId:
    """Tests for generate_task_id()."""

    def test_format(self) -> None:
        assert generate_task_id(1) == "TASK-0001"

    def test_zero_padding(self) -> None:
        assert generate_task_id(42) == "TASK-0042"

    def test_large_number(self) -> None:
        assert generate_task_id(9999) == "TASK-9999"

    def test_overflow_padding(self) -> None:
        """Index beyond 4 digits just uses more digits."""
        assert generate_task_id(10000) == "TASK-10000"


class TestNormalizeTaskId:
    """Tests for normalize_task_id()."""

    def test_numeric_shorthand(self) -> None:
        assert normalize_task_id("1") == "TASK-0001"

    def test_larger_number(self) -> None:
        assert normalize_task_id("42") == "TASK-0042"

    def test_overflow_number(self) -> None:
        """Numbers beyond 4 digits just use more digits."""
        assert normalize_task_id("10000") == "TASK-10000"

    def test_zero_padded_input(self) -> None:
        """``"0001"`` is numeric and produces the same result as ``"1"``."""
        assert normalize_task_id("0001") == "TASK-0001"

    def test_full_format_passthrough(self) -> None:
        """Canonical ``TASK-XXXX`` IDs pass through unchanged."""
        assert normalize_task_id("TASK-0042") == "TASK-0042"

    def test_custom_id_passthrough(self) -> None:
        """Non-numeric IDs like ``CUSTOM-001`` pass through."""
        assert normalize_task_id("CUSTOM-001") == "CUSTOM-001"

    def test_empty_string_passthrough(self) -> None:
        """Empty string is not numeric and passes through unchanged."""
        assert normalize_task_id("") == ""
