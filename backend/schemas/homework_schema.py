"""作业 Pydantic 模型"""

from typing import Optional

from pydantic import BaseModel


class HomeworkCreate(BaseModel):
    class_id: int
    content: str
    type: str = "daily"
    due_date: Optional[str] = None
    note: Optional[str] = None


class HomeworkStatusUpdate(BaseModel):
    status: str
