"""记录 Pydantic 模型"""

from typing import Optional

from pydantic import BaseModel


class RecordCreate(BaseModel):
    student_id: int
    type: str   # attendance / leave / score
    content: Optional[str] = None
    value: Optional[float] = None


class RecordOut(BaseModel):
    id: int
    student_id: int
    type: str
    content: Optional[str] = None
    value: Optional[float] = None
    created_at: Optional[str] = None
