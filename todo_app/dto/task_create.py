# 创建任务输入：title, description, priority
from pydantic import BaseModel, Field

class CreateTaskDTO(BaseModel):
    """
    创建任务的输入。

    校验规则（Pydantic 构造时自动执行）：
    - title: 必填，1-200 字符
    - description: 可选，最长 2000
    - priority: 可选，0-3
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: int = Field(default=0, ge=0, le=3)