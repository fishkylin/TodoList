# `todo show TASK-0001`
import typer
from typing import Annotated
from todo_app.exceptions import StorageError, TaskNotFoundError
from todo_app.dest import get_service
from rich.console import Console
from rich.panel import Panel
from rich.table import Table as InnerTable

def show(
        ctx: typer.Context,
        task_id: Annotated[str, typer.Argument(help="Task ID")]
    ) -> None:
    service = get_service(ctx)
    t = ctx.obj["texts"]

    try:
        task = service.get_task_detail(task_id)
    except StorageError:
        typer.secho(t["error"]["storage"], fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except TaskNotFoundError:
        typer.secho(t["error"]["not_found"].format(id=task_id), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    
    if not task:
        typer.echo(t["error"]["not_found"].format(id=task_id))
        
    # InnerTable(show_header=False, box=None) → 无表头无边框（用于详情布局）
    inner = InnerTable(show_header=False, box=None, padding=(0, 1))
    inner.add_column("Label", style="bold cyan", width=15)
    inner.add_column("Value", style="white")
    inner.add_row("Title", task.title)
    inner.add_row("Description", task.description or "N/A")
    inner.add_row("Status", "Done" if task.is_completed else "Pending")
    inner.add_row("Priority", str(task.priority))
    inner.add_row("Created", task.created_at)
    inner.add_row("Completed", task.completed_at or "Not yet")

    # Panel 包裹内嵌表格
    console = Console()
    console.print(Panel(inner, title=f"Task {task_id}", border_style="blue"))