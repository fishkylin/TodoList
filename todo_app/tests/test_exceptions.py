"""Tests for the custom exception hierarchy."""
import pytest

from todo_app.exceptions import TodoError, StorageError, TaskNotFoundError


class TestTodoError:
    """Tests for the base exception class."""

    def test_is_exception(self) -> None:
        assert issubclass(TodoError, Exception)

    def test_can_raise(self) -> None:
        with pytest.raises(TodoError):
            raise TodoError("generic")


class TestStorageError:
    """Tests for StorageError."""

    def test_is_todo_error(self) -> None:
        assert issubclass(StorageError, TodoError)

    def test_can_be_caught_as_todo_error(self) -> None:
        with pytest.raises(TodoError):
            raise StorageError("disk full")


class TestTaskNotFoundError:
    """Tests for TaskNotFoundError."""

    def test_is_todo_error(self) -> None:
        assert issubclass(TaskNotFoundError, TodoError)

    def test_carries_task_id_attribute(self) -> None:
        exc = TaskNotFoundError("TASK-0042")
        assert exc.task_id == "TASK-0042"

    def test_message_includes_task_id(self) -> None:
        exc = TaskNotFoundError("TASK-0042")
        assert "TASK-0042" in str(exc)
        assert "not found" in str(exc)

    def test_can_be_caught_as_todo_error(self) -> None:
        with pytest.raises(TodoError) as exc_info:
            raise TaskNotFoundError("TASK-0099")
        assert exc_info.value.task_id == "TASK-0099"  # type: ignore[attr-defined]

    def test_empty_task_id(self) -> None:
        exc = TaskNotFoundError("")
        assert exc.task_id == ""
        assert "not found" in str(exc)
