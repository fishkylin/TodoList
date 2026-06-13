# 自定义异常：TodoError → StorageError / TaskNotFoundError
class TodoError(Exception):
    """所有自定义异常的基类。捕获时可以 catch TodoError 兜底。"""

class StorageError(TodoError):
    """JSON 读写失败（文件损坏、磁盘满、权限不足等）。"""

class TaskNotFoundError(TodoError):
    """按 ID 查找任务时不存在。携带 task_id 便于日志追查。"""
    def __init__(self, task_id: str):
        self.taskid = task_id
        super().__init__(f"Task '{task_id}' not found")