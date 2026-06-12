# Task 数据类 + TaskStatus 枚举 + generate_task_id()
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending" # 未完成 - 任务初始状态
    COMPLETED = "completed" # 已完成 - 用户标记后

class Task(BaseModel):
    """
        任务实体模型，用于表示一个待办/任务项。

        该模型主要用于 API 请求/响应以及持久化前的数据校验。任务的核心属性包括标题、
        描述、状态、优先级，以及自动记录的时间戳。ID 由持久化层（Repository）在
        首次保存时分配，创建时无需提供。

        Attributes:
            id (str): 任务的唯一标识。由 Repository 在持久化时分配，创建时传空字符串。
                默认值为 ""，表示尚未持久化或分配 ID。
            title (str): 任务标题。必填，长度 1-200 字符。
            description (str | None): 任务详细描述。可选，最大长度 2000 字符，默认为 None。
            status (str): 任务状态。值为 TaskStatus.PENDING（"pending"）或
                TaskStatus.COMPLETED（"completed"）。新建任务默认为 PENDING。
            priority (int): 优先级。取值范围 0~3（包含），0 最低，3 最高。默认 0。
            created_at (str): 任务创建时间（ISO 8601 格式 UTC 时间）。由 default_factory
                自动设置为实例化时的当前时间，无需手动传入。
            updated_at (str): 任务最后更新时间（ISO 8601 格式 UTC 时间）。同样自动
                设置为实例化时的当前时间，后续更新逻辑应手动修改此字段。
            completed (str | None): 任务实际完成的时间（ISO 8601 格式 UTC 时间）。
                仅在状态变为 COMPLETED 时由业务逻辑设置，默认为 None。

        Usage Example:
            创建新任务（不指定 id 和自动时间字段）：
            >>> task = Task(title="Review PR", description="Check code style", priority=1)
            >>> task.created_at  # 自动生成为当前 UTC 时间字符串

            保存后更新 id：
            >>> task.id = "task_123"

            标记完成：
            >>> task.status = TaskStatus.COMPLETED
            >>> task.completed = datetime.now(timezone.utc).isoformat()
            >>> task.updated_at = datetime.now(timezone.utc).isoformat()

        Note:
            - created_at 和 updated_at 使用 default_factory 且为字符串类型，
            确保每次实例化生成独立的时间戳，避免类定义时固定。
            - priority 的数字大小与优先级高低的映射关系由业务层解释，模型本身只保证值范围。
            - 当 status 为 COMPLETED 时，建议同时设置 completed 时间戳，便于追踪完成时刻。
    """
    id: str = Field(default="", description="由 Repository 持久化时分配，创建时可为空")
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: str = Field(default=TaskStatus.PENDING)
    priority: int = Field(default=0, ge=0, le=3)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed: str | None = Field(default=None)

    def mark_completed(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.status = TaskStatus.COMPLETED
        self.updated_at = now
        self.completed = now

    def mark_pending(self) -> None:
        self.status = TaskStatus.PENDING
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self.completed = None

def generate_task_id(index: int) -> str:
    return f"TASK-{index:04d}"