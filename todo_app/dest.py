"""Dependency access helpers for Typer commands.

These thin accessors provide typed retrieval of shared objects from
the Typer context (ctx.obj) — keeping commands clean and decoupled
from the context dict layout.
"""
from typing import Any, cast

import typer

from todo_app.services.task_service import TaskService


def get_service(ctx: typer.Context) -> TaskService:
    """Return the TaskService instance from the Typer context."""
    return cast(TaskService, ctx.obj["service"])


def get_texts(ctx: typer.Context) -> dict[str, Any]:
    """Return the i18n text dictionary from the Typer context."""
    return cast(dict[str, Any], ctx.obj["texts"])
