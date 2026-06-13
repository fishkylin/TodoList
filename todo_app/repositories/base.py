# TaskRepository 抽象接口（6 个抽象方法）
from abc import ABC, abstractmethod
from todo_app.models.task import Task

class TaskRepository(ABC):
    """
    存储抽象接口 —— Service 只依赖这个接口，不依赖 JSON 或 SQLite。

    为什么用 ABC：
    - @abstractmethod 强制子类实现所有方法
    - 子类缺方法时实例化会报 TypeError（不是运行时才发现）
    """
    @abstractmethod
    def get_all(self) -> list[Task]:
        """获取任务列表。
        Returns:
            任务列表对象。
        """
        ...
    @abstractmethod
    def get_by_id(self, task_id: str) -> Task | None:
        """根据任务 ID 获取任务。
        Args:
            task_id: 任务的唯一标识符（格式如 "TASK-0001"）。
        Returns:
            找到的任务对象，如果不存在则返回 None。
        """
        ...
    @abstractmethod
    def add(self, task: Task) -> Task:
        """添加任务。
        Args:
            task: 任务对象
        Returns:
            成功添加的任务对象。
        """
        ...
    @abstractmethod
    def update(self, task: Task) -> Task: ...
    @abstractmethod
    def delete(self, task_id: str) -> bool: ...
    @abstractmethod
    def count(self) -> int:
        """返回当前存储的任务总数。"""
        ...