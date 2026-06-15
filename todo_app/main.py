# ★ 程序入口：Typer 应用定义 + 全局回调（依赖组）
import typer
from typing import Annotated


from todo_app.config import Settings
from todo_app.language import get_texts
from todo_app.repositories.json_repo import JsonTaskRepository
from todo_app.services.task_service import TaskService
from todo_app.commands.add import add as add_cmd
from todo_app.commands.list import list_tasks as list_cmd


app = typer.Typer(
    name="todo",
    help="Todo CLI — Manage your tasks from the terminal.",
    no_args_is_help=True
)

@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    lang: Annotated[str, typer.Option("--lang", help="Language (en/zh)")] = "en",
    debug: Annotated[bool, typer.Option("--debug", help="Debug Model")] = False,
) -> None:
    """
    全局回调 — 所有子命令执行前运行。

    "依赖组装工厂"：
    1. 读配置（Settings 自动读 .env）
    2. 创建存储（阶段 5 换成 JsonTaskRepository）
    3. 创建服务
    4. 注入 Typer 上下文 → 命令函数通过 ctx.obj 获取
    """
    settings = Settings()
    effective_lang = lang if lang != "en" else settings.language

    ctx.ensure_object(dict)
    ctx.obj["service"] = TaskService(JsonTaskRepository(settings.data_file))
    ctx.obj["texts"] = get_texts(effective_lang)


app.command(name="add")(add_cmd)
app.command(name="list")(list_cmd)

if __name__ == "__main__":
    app()
