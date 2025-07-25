from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

class MeetingBase(BaseModel):
    start_time: datetime
    end_time: datetime
    booked_by_email: EmailStr
    meeting_type: constr(regex="^(virtual|in-person)$")
    travel_time_before: Optional[int] = 0
    travel_time_after: Optional[int] = 0
    virtual_app: Optional[str] = None

class MeetingCreate(MeetingBase):
    agenda_id: int

class MeetingResponse(MeetingBase):
    id: int
    status: str
    is_external: Optional[bool] = False

    class Config:
        orm_mode = True 