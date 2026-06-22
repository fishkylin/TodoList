from typing import cast, Any
import typer

from todo_app.services.task_service import TaskService

def get_service(ctx: typer.Context) -> TaskService:
    return cast(TaskService, ctx.obj["service"])

def get_texts(ctx: typer.Context) -> dict[str, Any]:
    return cast(dict[str, Any], ctx.obj["texts"])