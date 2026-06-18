# `todo delete TASK-0001`
import typer
from typing import Annotated
from todo_app.dest import get_service
from todo_app.exceptions import TaskNotFoundError


def delete_task(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    force: Annotated[bool, typer.Option("-f", "--force")] = False
) -> None:
    service = get_service(ctx)
    t = ctx.obj["texts"]

    try:
        task = service.get_task_detail(task_id)
    except TaskNotFoundError:
        typer.secho(t["error"]["not_found"].format(id=task_id), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not force:
        confirmed = typer.confirm(f"Delete '{task.title}' (ID: {task.id})?", default=False)
        if not confirmed:
            raise typer.Abort()

    service.delete_task(task_id)
    typer.echo(f"Task '{task.title}' deleted.")