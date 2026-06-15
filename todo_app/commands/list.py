# `todo list`
import typer
from typing import Annotated
from todo_app.exceptions import StorageError
from todo_app.dest import get_service

def list_tasks(
    ctx: typer.Context,
    show_all: Annotated[bool, typer.Option("-a", "--all")] = False
) -> None:
    """列出任务。默认隐藏已完成的。"""
    service = get_service(ctx)
    t = ctx.obj["texts"]

    try:
        tasks = service.list_tasks(include_completed=show_all)
    except StorageError:
        typer.secho(t["error"]["storage"], fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not tasks:
        typer.echo(t["prompt"]["no_tasks"])
        return

    for task in tasks:
        icon = t["status"]["done"] if task.is_completed else t["status"]["pending"]
        typer.echo(f"   {task.id}  {icon}  {task.title}")
