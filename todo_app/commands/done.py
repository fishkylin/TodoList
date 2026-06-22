"""``todo done`` — toggle task completion status."""
import typer
from typing import Annotated

from todo_app.dest import get_service, get_texts
from todo_app.exceptions import TaskNotFoundError
from todo_app.logger import get_logger

logger = get_logger(__name__)


def done(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="Task ID")],
) -> None:
    """Toggle task status: pending → completed, or completed → pending."""
    service = get_service(ctx)
    t = get_texts(ctx)

    try:
        current = service.get_task_detail(task_id)
    except TaskNotFoundError:
        logger.warning("Toggle failed — task %s not found", task_id)
        typer.secho(t["error"]["not_found"].format(id=task_id), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if current.is_completed:
        service.uncomplete_task(task_id)
        typer.echo(t["task"]["reopened"].format(id=task_id))
    else:
        service.complete_task(task_id)
        typer.echo(t["task"]["completed"].format(id=task_id))
