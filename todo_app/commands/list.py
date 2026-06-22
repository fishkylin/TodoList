"""``todo list`` — display tasks in a rich table."""
import typer
from typing import Annotated

from rich.console import Console
from rich.table import Table
from rich.text import Text

from todo_app.dest import get_service, get_texts
from todo_app.exceptions import StorageError
from todo_app.logger import get_logger

logger = get_logger(__name__)


def list_tasks(
    ctx: typer.Context,
    show_all: Annotated[bool, typer.Option("-a", "--all")] = False,
) -> None:
    """List tasks.  Completed tasks are hidden by default."""
    service = get_service(ctx)
    t = get_texts(ctx)

    try:
        tasks = service.list_tasks(include_completed=show_all)
    except StorageError:
        logger.exception("Storage error while listing tasks")
        typer.secho(t["error"]["storage"], fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not tasks:
        typer.echo(t["prompt"]["no_tasks"])
        return

    console = Console()
    table = Table(title=t["list"]["title"], title_style="bold white")
    table.add_column(t["table"]["header_id"], style="cyan", width=12, no_wrap=True)
    table.add_column(t["table"]["header_title"], width=40, overflow="fold")
    table.add_column(t["table"]["header_status"], width=8, justify="center")

    for task in tasks:
        icon = t["status"]["done"] if task.is_completed else t["status"]["pending"]
        color = "green bold" if task.is_completed else "red bold"
        table.add_row(
            task.id,
            Text(task.title, style=color, overflow="fold"),
            Text(icon, style=color),
        )

    console.print(table)
