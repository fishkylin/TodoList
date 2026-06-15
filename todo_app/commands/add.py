# `todo add "Buy milk"`
import typer
from typing import Annotated
from pydantic import ValidationError as PydanticError
from todo_app.dto.task_create import CreateTaskDTO
from todo_app.exceptions import StorageError
from todo_app.dest import get_service


def add(
    ctx: typer.Context,
    title: Annotated[str, typer.Argument(help="Task title")],
    description: Annotated[str | None, typer.Option("-d", "--description")] = None,
    priority: Annotated[int, typer.Option("-p", "--priority", min=0, max=3)] = 0
) -> None:
    """添加新任务。

    示例:
        todo add "Buy milk"
        todo add "Report" -d "Due Friday" -p 2
    """
    service = get_service(ctx)
    t = ctx.obj["texts"]

    try:
        # CreateTaskDTO 构造时 Pydantic 自动校验
        dto = CreateTaskDTO(title=title, description=description, priority=priority)
        result = service.add_task(dto)
        typer.echo(t["task"]["added"].format(title=result.title, id=result.id))

    except PydanticError as e:
        # Pydantic 校验失败 → 从 e.errors() 提取具体字段和原因
        for err in e.errors():
            field = ".".join(str(x) for x in err["loc"])
            typer.secho(f"Error: {field} — {err['msg']}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)
    except StorageError:
            typer.secho(t["error"]["storage"], fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)
                