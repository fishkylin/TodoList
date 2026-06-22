"""``todo edit`` — update task fields."""
import typer
from typing import Annotated

from todo_app.dest import get_service, get_texts
from todo_app.dto.task_update import UpdateTaskDTO
from todo_app.exceptions import TaskNotFoundError
from todo_app.logger import get_logger

logger = get_logger(__name__)


def edit(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help='Task ID (or numeric shorthand, e.g. "1")')],
    title: Annotated[str | None, typer.Option("-t", "--title", help="New title")] = None,
    description: Annotated[str | None, typer.Option("-d", "--description", help="New description")] = None,
    priority: Annotated[int | None, typer.Option("-p", "--priority", help="New priority (0-3)")] = None,
) -> None:
    """Partially update a task.  Only the provided fields are changed."""
    service = get_service(ctx)
    t = get_texts(ctx)

    if title is None and description is None and priority is None:
        typer.secho(t["edit"]["no_fields_error"], fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    try:
        dto = UpdateTaskDTO(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
        )
        service.update_task(dto)
        typer.echo(t["task"]["updated"].format(id=task_id))
    except TaskNotFoundError:
        logger.warning("Update failed — task %s not found", task_id)
        typer.secho(t["error"]["not_found"].format(id=task_id), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
