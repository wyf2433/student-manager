"""课表 Pydantic 模型"""

from typing import Optional

from pydantic import BaseModel


class ScheduleCreate(BaseModel):
    weekday: int
    period: int
    subject: str = "物理"
    class_name: Optional[str] = None


class ScheduleUpdate(BaseModel):
    weekday: Optional[int] = None
    period: Optional[int] = None
    subject: Optional[str] = None
    class_name: Optional[str] = None


class OverrideCreate(BaseModel):
    date: str
    period: int
    action: str
    new_subject: Optional[str] = None
    new_class_name: Optional[str] = None
    note: Optional[str] = None
