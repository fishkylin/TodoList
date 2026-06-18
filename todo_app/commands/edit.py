 # `todo edit TASK-0001 -t "new"`
import typer
from typing import Annotated
from todo_app.exceptions import TaskNotFoundError
from todo_app.dest import get_service
from todo_app.dto.task_update import UpdateTaskDTO

def edit(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    title: Annotated[str | None, typer.Option("-t", "--title", help="Task title")] = None,
    description: Annotated[str | None, typer.Option("-d", "--description", help="Task Description")] = None,
    priority: Annotated[int | None, typer.Option("-p", "--priority", help="Task Priority")] = None
) -> None:
    service = get_service(ctx)
    t = ctx.obj["texts"]
    if title is None and description is None and priority is None:
        typer.secho("Error: At least one field (-t, -d, -p) must be provided for update.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    try:
        dto = UpdateTaskDTO(
            task_id = task_id,
            title = title,
            description = description,
            priority = priority
        )
        service.update_task(dto)
        typer.echo(t["task"]["updated"].format(id=task_id))
    except TaskNotFoundError:
        typer.secho(t["error"]["not_found"].format(id=task_id), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    