"""速记 Pydantic 模型"""

from typing import Optional

from pydantic import BaseModel


class NoteCreate(BaseModel):
    content: str
    student_id: Optional[int] = None


class NoteUpdateStudent(BaseModel):
    student_id: int


class NoteOut(BaseModel):
    id: int
    content: str
    student_id: Optional[int] = None
    created_at: Optional[str] = None
