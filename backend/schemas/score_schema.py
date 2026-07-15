"""成绩 Pydantic 模型"""

from typing import Optional

from pydantic import BaseModel


class ScoreCreate(BaseModel):
    student_id: int
    exam_name: str
    subject: str
    score: Optional[float] = None


class ScoreImportConfirm(BaseModel):
    exam_name: str
    subject: str
    class_id: int
    students: list  # [{student_id(可选), name(可选), score}]
