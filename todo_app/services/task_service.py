# 7 个方法：增删改查完成取消
from todo_app.repositories.base import TaskRepository
from todo_app.dto.task_create import CreateTaskDTO
from todo_app.dto.task_update import UpdateTaskDTO
from todo_app.dto.task_response import TaskResponseDTO
from todo_app.exceptions import TaskNotFoundError
from todo_app.models.task import Task, TaskStatus
class TaskService:
    """
    业务逻辑层。

    设计原则：
    - 构造函数只接受 TaskRepository 接口——不依赖具体存储
    - 所有方法的输入是 DTO，输出也是 DTO——隔离内外
    - 不写 validate_xxx() —— Pydantic 在 DTO 构造时已完成校验
    """
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def add_task(self, dto: CreateTaskDTO) -> TaskResponseDTO:
        task = Task(
            title=dto.title,
            description=dto.description,
            priority=dto.priority
        )
        saved_task = self.repo.add(task)
        return TaskResponseDTO.from_task(saved_task)

    def list_tasks(self, *, include_completed: bool = True) -> list[TaskResponseDTO]:
        tasks = self.repo.get_all()
        if not include_completed:
            tasks = [t for t in tasks if t.status != TaskStatus.COMPLETED]
        return [TaskResponseDTO.from_task(t) for t in tasks]

    def get_task_detail(self, task_id: str) -> TaskResponseDTO:
        task = self.repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"找不到ID：{task_id}的任务")
        return TaskResponseDTO.from_task(task)
    
    def complete_task(self, task_id: str) -> TaskResponseDTO:
        task = self.repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"找不到ID：{task_id}的任务")
        task.mark_completed()
        return TaskResponseDTO.from_task(task)

    def uncomplete_task(self, task_id: str) -> TaskResponseDTO:
        task = self.repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"找不到ID：{task_id}的任务")
        task.mark_pending()
        return TaskResponseDTO.from_task(task)

    def delete_task(self, task_id: str) -> bool:
        deleted = self.repo.delete(task_id)
        if not deleted:
            raise TaskNotFoundError(f"找不到ID：{task_id}的任务")
        return True

    def update_task(self, dto: UpdateTaskDTO) -> TaskResponseDTO:
        task = self.repo.get_by_id(dto.task_id)
        if task is None:
            raise TaskNotFoundError(f"找不到ID：{dto.task_id}的任务")
        updates = dto.model_dump(exclude_none=True)
        for field, value in updates.items():
            if field != 'task_id':
                setattr(task, field, value)
        return TaskResponseDTO.from_task(task)