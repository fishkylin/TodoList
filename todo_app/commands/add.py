# commands/add.py
# CLI command for listing tasks
import typer
from typing import Annotated
from pydantic import ValidationError as PydanticError

from todo_app.dto.task_create import CreateTaskDTO
from todo_app.exceptions import StorageError
from todo_app.dest import get_service, get_texts
from todo_app.logger import get_logger

logger = get_logger(__name__)


def add(
    ctx: typer.Context,
    title: Annotated[str, typer.Argument(help="Task title")],
    description: Annotated[str | None, typer.Option("-d", "--description")] = None,
    priority: Annotated[int, typer.Option("-p", "--priority", min=0, max=3)] = 0
) -> None:
    """
    Add task

    Examples:
        todo add "task title" -d "description" -p "priority"
    """
    service = get_service(ctx)
    t = get_texts(ctx)

    try:
        dto = CreateTaskDTO(title=title, description=description, priority=priority)
        result = service.add_task(dto)
        typer.echo(t["task"]["added"].format(title=result.title, id=result.id))

    except PydanticError as e:
        logger.warning(f"Validation error for title='{title}: {e.errors()}'")
        for err in e.errors():
            field = ".".join(str(x) for x in err["loc"])
            typer.secho(f"Error: {field} — {err['msg']}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)
    except StorageError as e:
            logger.error(f"Storage error while adding task: {e}", exc_info=True)
            typer.secho(t["error"]["storage"], fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)
                