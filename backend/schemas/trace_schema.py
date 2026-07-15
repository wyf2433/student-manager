"""工作留痕 Pydantic 模型"""

from typing import Optional

from pydantic import BaseModel


class TraceCreate(BaseModel):
    title: str
    type: str
    note: Optional[str] = None
    image_urls: Optional[list] = None
    student_ids: Optional[list] = None


class TraceUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    note: Optional[str] = None
    image_urls: Optional[list] = None
    student_ids: Optional[list] = None
