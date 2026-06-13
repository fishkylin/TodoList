# 更新任务输入：task_id + 要改的字段
from pydantic import BaseModel, Field

class UpdateTaskDTO(BaseModel):
    """
    更新任务的输入。

    所有字段（除 task_id）默认为 None —— 表示"不修改"。
    只有用户显式传入的字段才会被更新。
    """
    task_id: str = Field(..., min_length=1)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: int | None = Field(default=None, ge=0, le=3)
