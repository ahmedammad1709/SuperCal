from pydantic import BaseModel
from typing import Optional

class CalendarBase(BaseModel):
    alias: str
    sync_direction: Optional[str] = "one-way"
    subject_prefix: Optional[str] = None

class CalendarCreate(CalendarBase):
    is_primary: Optional[bool] = False
    sync_direction: Optional[str] = "one-way"
    subject_prefix: Optional[str] = None

class CalendarUpdate(BaseModel):
    alias: Optional[str] = None
    is_primary: Optional[bool] = None
    sync_direction: Optional[str] = None
    subject_prefix: Optional[str] = None

class CalendarResponse(CalendarBase):
    id: int
    is_primary: bool
    sync_direction: Optional[str] = "one-way"
    subject_prefix: Optional[str] = None

    class Config:
        orm_mode = True 