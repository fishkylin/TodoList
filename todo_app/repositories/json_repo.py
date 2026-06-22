"""JSON-file task repository with atomic writes."""
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from todo_app.exceptions import StorageError, TaskNotFoundError
from todo_app.logger import get_logger
from todo_app.models.task import Task, generate_task_id
from todo_app.repositories.base import TaskRepository

logger = get_logger(__name__)


class JsonTaskRepository(TaskRepository):
    """Persist tasks to a single JSON file on disk.

    Internal file structure::

        {"tasks": [{task_dict}, ...], "meta": {"next_index": 5}}

    Writes are atomic (temp file → rename → cleanup) to avoid
    corrupting the data file on partial failures.
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug("JsonTaskRepository initialised (file=%s)", file_path)

    # ── private helpers ─────────────────────────────────────────────

    def _load_data(self) -> dict[str, Any]:
        """Load task data from the JSON file.

        Returns a clean default on first run; auto-repairs on corruption.
        """
        default: dict[str, Any] = {"tasks": [], "meta": {"next_index": 1}}
        corrupted = False

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data: Any = json.load(f)
        except FileNotFoundError:
            logger.debug("No existing data file — starting fresh")
            return default
        except (UnicodeDecodeError, json.JSONDecodeError):
            logger.warning("Data file corrupted, resetting to empty")
            corrupted = True
        except OSError as e:
            logger.exception("Failed to read task data")
            raise StorageError("Could not read task data.") from e

        if corrupted:
            self._save_data(default)
            return default

        if not isinstance(data, dict):
            logger.warning("Unexpected JSON root type (%s), resetting", type(data).__name__)
            self._save_data(default)
            return default

        return data

    def _save_data(self, data: dict[str, Any]) -> None:
        """Atomically write data to disk."""
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

            shutil.move(str(tmp_path), str(self.file_path))
            logger.debug("Data saved (%d tasks)", len(data.get("tasks", [])))
        except OSError as e:
            logger.exception("Failed to save task data")
            raise StorageError("Could not save task data.") from e
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()

    # ── public interface ────────────────────────────────────────────

    def get_all(self) -> list[Task]:
        logger.debug("Loading all tasks")
        data = self._load_data()
        tasks = [Task.model_validate(t) for t in data["tasks"]]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        logger.debug("Loaded %d task(s)", len(tasks))
        return tasks

    def get_by_id(self, task_id: str) -> Task | None:
        logger.debug("Looking up task %s", task_id)
        data = self._load_data()
        for t in data["tasks"]:
            if t.get("id") == task_id:
                logger.debug("Task %s found", task_id)
                return Task.model_validate(t)
        logger.debug("Task %s not found", task_id)
        return None

    def add(self, task: Task) -> Task:
        data = self._load_data()
        if task.id == "":
            task.id = generate_task_id(data["meta"]["next_index"])
            data["meta"]["next_index"] += 1
        data["tasks"].append(task.model_dump())
        self._save_data(data)
        logger.info("Task %s added — %d total", task.id, len(data["tasks"]))
        return task

    def update(self, task: Task) -> Task:
        data = self._load_data()
        tasks = data.get("tasks", [])
        for idx, t_dict in enumerate(tasks):
            if t_dict.get("id") == task.id:
                tasks[idx] = task.model_dump()
                self._save_data(data)
                logger.info("Task %s updated", task.id)
                return task
        logger.warning("Task %s not found for update", task.id)
        raise TaskNotFoundError(task.id)

    def delete(self, task_id: str) -> bool:
        data = self._load_data()
        old_len = len(data.get("tasks", []))
        new_tasks = [t for t in data["tasks"] if t.get("id") != task_id]
        data["tasks"] = new_tasks
        self._save_data(data)

        deleted = old_len > len(new_tasks)
        if deleted:
            logger.info("Task %s deleted — %d remaining", task_id, len(new_tasks))
        else:
            logger.debug("Task %s not found for deletion", task_id)
        return deleted

    def count(self) -> int:
        return len(self._load_data()["tasks"])
