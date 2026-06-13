# 任务输出：给命令层渲染用
from pydantic import BaseModel
from todo_app.models.task import Task, TaskStatus

class TaskResponseDTO(BaseModel):
    """
    任务输出——给命令层渲染用。

    is_completed 是便捷字段：从 status 推导而来。
    命令层不需要自己判断 TaskStatus 枚举。
    """
    id: str
    title: str
    description: str | None
    status: str              # TaskStatus.value → "pending" / "completed"
    priority: int
    created_at: str
    completed_at: str | None
    is_completed: bool

    @classmethod
    def from_task(cls, task: Task) -> "TaskResponseDTO":
        """从领域模型构建输出 DTO。"""
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            created_at=task.created_at,
            completed_at=task.completed_at,
            is_completed=(task.status == TaskStatus.COMPLETED)
        )