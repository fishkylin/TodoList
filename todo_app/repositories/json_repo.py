# JSON 文件实现（读写 ~/.todo/tasks.json）
import json, tempfile, shutil
from pathlib import Path
from typing import Any

from todo_app.repositories.base import TaskRepository
from todo_app.models.task import Task, generate_task_id
from todo_app.exceptions import StorageError, TaskNotFoundError
# from todo_app.logger import get_logger

# logger = get_logger(__name__)

class JsonTaskRepository(TaskRepository):
    """
    JSON 文件持久化。

    内部文件结构:
        {"tasks": [{task_dict}, ...], "meta": {"next_index": 5}}

    为什么 _load_data / _save_data 是私有方法：
    - 外部只需要 get_all/add/delete 等，不需要知道 JSON 长什么样
    - 未来改成 SQLite 时，这些私有方法会被完全替换，公开方法签名不变
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    # ── 私有方法 ──

    def _load_data(self) -> dict[str, Any]:
        """读 JSON 文件，处理损坏和结构异常。

        当数据损坏时自动写入一份干净的默认数据，避免只读方法（get_all/count）
        每次调用都因为未修复的损坏文件而重复降级。
        """
        default: dict[str, Any] = {"tasks": [], "meta": {"next_index": 1}}
        data: Any = None
        corrupted = False

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return default
        except (UnicodeDecodeError, json.JSONDecodeError):
            # logger.warning("Data file corrupted, resetting to empty")
            corrupted = True
        except OSError as e:
            # logger.exception("Failed to read task data")
            raise StorageError("Could not read task data.") from e

        if corrupted:
            self._save_data(default)
            return default

        # 合法 JSON 不一定是 dict（可能是 "hello"、[1,2,3]），防御一下
        if not isinstance(data, dict):
            self._save_data(default)
            return default

        return data

    def _save_data(self, data: dict[str, Any]) -> None:
        """原子写入：临时文件 → 重命名 → 清理。"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=str(self.file_path.parent),
                prefix=f"{self.file_path.name}.tmp_",
                suffix=".tmp",
                delete=False,
            ) as tmp_file:
                tmp_path = Path(tmp_file.name)
                json.dump(data, tmp_file, indent=2, ensure_ascii=False)
            # with 块结束 → 文件已关闭，但 delete=False 保留了文件
            shutil.move(str(tmp_path), str(self.file_path))
        except OSError as e:
            # logger.exception("Failed to save task data")
            raise StorageError("Could not save task data.") from e
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()
    # ── 公开方法 ──

    def get_all(self) -> list[Task]:
        data = self._load_data()
        tasks = [Task.model_validate(t) for t in data["tasks"]]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks

    def get_by_id(self, task_id: str) -> Task | None:
        data = self._load_data()
        for t in data["tasks"]:
            if t.get("id") == task_id:
                return Task.model_validate(t)
        return None

    def add(self, task: Task) -> Task:
        data = self._load_data()
        if task.id == "":
            task.id = generate_task_id(data["meta"]["next_index"])
            data["meta"]["next_index"] += 1
        data["tasks"].append(task.model_dump())
        self._save_data(data)
        return task

    def update(self, task: Task) -> Task:
        data = self._load_data()
        tasks = data.get("tasks", [])
        for idx, t_dict in enumerate(tasks):
            if t_dict.get("id") == task.id:
                tasks[idx] = task.model_dump()
                self._save_data(data)
                return task
        raise TaskNotFoundError(task.id)

    def delete(self, task_id: str) -> bool:
        data = self._load_data()
        tasks = data.get("tasks", [])
        old_len = len(tasks)
        new_tasks = [t for t in tasks if t.get("id") != task_id]
        data["tasks"] = new_tasks
        self._save_data(data)
        return old_len != len(tasks)
        
    def count(self) -> int:
        return len(self._load_data()["tasks"])
