"""``todo show`` — display detailed task information."""
import typer
from typing import Annotated

from rich.console import Console
from rich.panel import Panel
from rich.table import Table as InnerTable

from todo_app.dest import get_service, get_texts
from todo_app.exceptions import StorageError, TaskNotFoundError
from todo_app.logger import get_logger
from todo_app.utils import format_datetime

logger = get_logger(__name__)


def show(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help='Task ID (or numeric shorthand, e.g. "1")')],
) -> None:
    """Display full details for a single task."""
    service = get_service(ctx)
    t = get_texts(ctx)

    try:
        task = service.get_task_detail(task_id)
    except StorageError:
        logger.exception("Storage error while showing task %s", task_id)
        typer.secho(t["error"]["storage"], fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except TaskNotFoundError:
        logger.warning("Show failed — task %s not found", task_id)
        typer.secho(t["error"]["not_found"].format(id=task_id), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not task:
        typer.echo(t["error"]["not_found"].format(id=task_id))

    inner = InnerTable(show_header=False, box=None, padding=(0, 1))
    inner.add_column("Label", style="bold cyan", width=15)
    inner.add_column("Value", style="white")
    inner.add_row(t["show"]["label_title"], task.title)
    inner.add_row(t["show"]["label_description"], task.description or t["show"]["na"])
    inner.add_row(
        t["show"]["label_status"],
        t["show"]["status_done"] if task.is_completed else t["show"]["status_pending"],
    )
    inner.add_row(t["show"]["label_priority"], str(task.priority))
    inner.add_row(
        t["show"]["label_created"],
        format_datetime(iso_str=task.created_at, default=t["show"]["na"]),
    )
    inner.add_row(
        t["show"]["label_updated"],
        format_datetime(iso_str=task.updated_at, default=t["show"]["na"]),
    )
    inner.add_row(
        t["show"]["label_completed"],
        format_datetime(iso_str=task.completed_at, default=t["show"]["not_yet"]),
    )

    console = Console()
    console.print(Panel(inner, title=f"Task {task_id}", border_style="blue"))
