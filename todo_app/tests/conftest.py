"""Shared pytest fixtures."""
import pytest

from todo_app.repositories.memory_repo import MemoryTaskRepository
from todo_app.services.task_service import TaskService


@pytest.fixture
def memory_repo():
    """Return a fresh in-memory repository for each test."""
    return MemoryTaskRepository()


@pytest.fixture
def task_service(memory_repo):
    """Return a TaskService backed by an in-memory repository."""
    return TaskService(memory_repo)
