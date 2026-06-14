from todo_app.repositories.base import TaskRepository
from todo_app.models.task import Task, generate_task_id
from todo_app.exceptions import TaskNotFoundError

class MemoryTaskRepository(TaskRepository):
    """
    纯内存实现 —— 仅用于跑通链路和测试。

    内部用 list[Task] 存数据，_next_id 自增生成 TASK-0001 格式 ID。
    进程重启数据丢失——这是预期行为，阶段 5 用 JSON 持久化。
    """
    _tasks: list[Task] = []
    _next_id: int = 1
    
    def get_all(self) -> list[Task]:
        return sorted(self._tasks, key=lambda t: t.created_at, reverse=True)
    
    def get_by_id(self, task_id: str) -> Task | None:
        return next((t for t in self._tasks if  t.id == task_id), None)

    def add(self, task: Task) -> Task:
        if task.id == "":
            task.id = generate_task_id(self._next_id)
            self.__class__._next_id += 1
        self._tasks.append(task)
        return task
    
    def update(self, task: Task) -> Task:
        for i, t in enumerate(self._tasks):
            if t.id == task.id:
                self._tasks[i] = task
                return task
        raise TaskNotFoundError(task.id)

    def delete(self, task_id: str) -> bool:
        old_len = self.count()
        self._tasks[:] = [t for t in self._tasks if t.id != task_id]
        return old_len != self.count()
    
    def count(self) -> int:
        return len(self._tasks)