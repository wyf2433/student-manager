"""班级 Pydantic 模型"""

from typing import Optional

from pydantic import BaseModel


class ClassCreate(BaseModel):
    name: str
    grade: Optional[str] = None


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[str] = None


class ClassOut(BaseModel):
    id: int
    name: str
    grade: Optional[str] = None
    created_at: Optional[str] = None
