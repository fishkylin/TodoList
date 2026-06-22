"""Application entry point — Typer app definition and global callback.

The callback acts as a dependency-assembly factory:
    1. Load settings (from .env via Settings)
    2. Create repository (JsonTaskRepository)
    3. Create service (TaskService)
    4. Inject into Typer context so commands access them via ctx.obj
"""
import typer
from typing import Annotated

from todo_app.config import Settings
from todo_app.i18n import get_texts
from todo_app.repositories.json_repo import JsonTaskRepository
from todo_app.services.task_service import TaskService
from todo_app.commands.add import add as add_cmd
from todo_app.commands.list import list_tasks as list_cmd
from todo_app.commands.show import show as show_cmd
from todo_app.commands.delete import delete_task as delete_cmd
from todo_app.commands.done import done as done_cmd
from todo_app.commands.edit import edit as edit_cmd
from todo_app.logger import get_logger, setup_logging

app = typer.Typer(
    name="todo",
    help="Todo CLI — Manage your tasks from the terminal.",
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    lang: Annotated[str, typer.Option("--lang", help="Language (en / zh)")] = "en",
    debug: Annotated[bool, typer.Option("--debug", help="Enable debug mode")] = False,
) -> None:
    """Global callback — runs before every sub-command.

    Assembles dependencies:
    1. Load settings (Settings reads .env automatically)
    2. Create storage (JsonTaskRepository)
    3. Create service (TaskService)
    4. Inject into Typer context → commands retrieve via ctx.obj
    """
    settings = Settings()
    effective_lang = lang if lang != "en" else settings.language
    logger = get_logger(__name__)
    setup_logging("DEBUG" if debug else settings.log_level)
    logger.info("Todo CLI starting (lang=%s, debug=%s)", effective_lang, debug)

    ctx.ensure_object(dict)
    ctx.obj["service"] = TaskService(JsonTaskRepository(settings.data_file))
    ctx.obj["texts"] = get_texts(effective_lang)


app.command(name="add")(add_cmd)
app.command(name="list")(list_cmd)
app.command(name="show")(show_cmd)
app.command(name="delete")(delete_cmd)
app.command(name="done")(done_cmd)
app.command(name="edit")(edit_cmd)

if __name__ == "__main__":
    app()
