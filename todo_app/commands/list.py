# `todo list`
import typer
from typing import Annotated
from todo_app.exceptions import StorageError
from todo_app.dest import get_service
from rich.console import Console
from rich.table import Table
from rich.text import Text
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

    console = Console()
    table = Table(title="My Tasks", title_style="bold white")
    table.add_column("ID", style="cyan", width=12, no_wrap=True)
    table.add_column("Title", width=40, overflow="fold")
    table.add_column("Status", width=8, justify="center")
    for task in tasks:
        icon = t["status"]["done"] if task.is_completed else t["status"]["pending"]
        color = "green bold" if task.is_completed else "red bold"
        table.add_row(
            task.id,
            Text(task.title, style=color, overflow="fold"),
            Text(icon, style=color)
        )
    console.print(table)