# 7 个方法：增删改查完成取消
from todo_app.repositories.base import TaskRepository
from todo_app.dto.task_create import CreateTaskDTO
from todo_app.dto.task_update import UpdateTaskDTO
from todo_app.dto.task_response import TaskResponseDTO
from todo_app.exceptions import TaskNotFoundError
from todo_app.models.task import Task
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

    def list_tasks(self, *, include_completed=True) -> list[TaskResponseDTO]:
        pass