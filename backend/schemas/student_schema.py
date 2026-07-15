"""学生 Pydantic 模型"""

from typing import Optional

from pydantic import BaseModel


class StudentCreate(BaseModel):
    class_id: int
    name: str
    student_no: Optional[str] = None
    gender: Optional[str] = None


class StudentBatchCreate(BaseModel):
    students: list[StudentCreate]


class StudentUpdate(BaseModel):
    class_id: Optional[int] = None
    name: Optional[str] = None
    student_no: Optional[str] = None
    gender: Optional[str] = None


class StudentOut(BaseModel):
    id: int
    class_id: int
    name: str
    student_no: Optional[str] = None
    gender: Optional[str] = None
    created_at: Optional[str] = None
