"""成绩 Pydantic 模型"""

from typing import Optional

from pydantic import BaseModel


class ScoreCreate(BaseModel):
    student_id: int
    exam_name: str
    subject: str
    score: Optional[float] = None
    full_score: Optional[float] = 100


class ScoreImportConfirm(BaseModel):
    exam_name: str
    class_id: Optional[int] = None
    grade_prefix: Optional[str] = None
    full_scores: Optional[dict] = None  # {科目: 满分}, 如 {"物理": 100, "语文": 150}
    students: list  # [{name, class_name(可选), grade(可选), scores: {科目: 分数}}]
