"""``todo delete`` — remove a task by ID."""
import typer
from typing import Annotated

from todo_app.dest import get_service, get_texts
from todo_app.exceptions import TaskNotFoundError
from todo_app.logger import get_logger

logger = get_logger(__name__)


def delete_task(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help='Task ID (or numeric shorthand, e.g. "1")')],
    force: Annotated[bool, typer.Option("-f", "--force")] = False,
) -> None:
    """Delete a task.  Prompts for confirmation unless ``--force`` is used."""
    service = get_service(ctx)
    t = get_texts(ctx)

    try:
        task = service.get_task_detail(task_id)
    except TaskNotFoundError:
        logger.warning("Delete failed — task %s not found", task_id)
        typer.secho(t["error"]["not_found"].format(id=task_id), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not force:
        confirmed = typer.confirm(
            t["prompt"]["confirm_delete"].format(title=task.title, id=task.id),
            default=False,
        )
        if not confirmed:
            logger.debug("Delete cancelled by user for task %s", task_id)
            raise typer.Abort()

    deleted = service.delete_task(task_id)
    if deleted:
        typer.echo(t["task"]["deleted"].format(title=task.title, id=task.id))
    else:
        logger.warning("Delete failed — task %s disappeared before deletion", task_id)
        typer.secho(t["error"]["not_found"].format(id=task_id), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
