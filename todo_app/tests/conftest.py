"""Shared pytest fixtures."""
from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from todo_app.models.task import Task
from todo_app.repositories.json_repo import JsonTaskRepository
from todo_app.repositories.memory_repo import MemoryTaskRepository
from todo_app.services.task_service import TaskService


# ── helper factories ──────────────────────────────────────────────────

def make_task(
    title: str = "Test Task",
    description: str = "A test task",
    priority: int = 0,
) -> Task:
    """Create a fresh Task instance with default values."""
    return Task(
        title=title,
        description=description,
        priority=priority,
    )


# ── memory repository fixtures ────────────────────────────────────────

@pytest.fixture
def memory_repo() -> MemoryTaskRepository:
    """Return a fresh in-memory repository for each test."""
    return MemoryTaskRepository()


@pytest.fixture
def task_service(memory_repo: MemoryTaskRepository) -> TaskService:
    """Return a TaskService backed by an in-memory repository."""
    return TaskService(memory_repo)


# ── JSON repository fixtures ──────────────────────────────────────────

@pytest.fixture
def json_repo() -> Generator[JsonTaskRepository, None, None]:
    """Return a JsonTaskRepository pointing to a temporary file.

    The file is deleted before constructing the repo so it starts from
    a genuinely clean (non-existent) state.
    """
    fd, tmp_name = tempfile.mkstemp(suffix=".json")
    tmp_path = Path(tmp_name)
    os.close(fd)  # We only need the name, not the open file handle
    tmp_path.unlink()  # Delete so _load_data hits FileNotFoundError first
    repo = JsonTaskRepository(tmp_path)
    yield repo
    # Cleanup
    tmp_path.unlink(missing_ok=True)


@pytest.fixture
def json_task_service(json_repo: JsonTaskRepository) -> TaskService:
    """Return a TaskService backed by a temporary JSON repository."""
    return TaskService(json_repo)
