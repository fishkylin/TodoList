from typing import cast
import typer

from todo_app.services.task_service import TaskService

def get_service(ctx: typer.Context) -> TaskService:
    return cast(TaskService, ctx.obj["service"])