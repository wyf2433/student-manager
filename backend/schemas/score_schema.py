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
    class_id: Optional[int] = None
    grade_prefix: Optional[str] = None
    students: list  # [{name, class_name(可选), score}]
