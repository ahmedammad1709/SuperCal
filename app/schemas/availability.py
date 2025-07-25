from pydantic import BaseModel, conint, constr
from typing import Optional

class AvailabilitySlotBase(BaseModel):
    day_of_week: conint(ge=0, le=6)
    start_time: constr(regex=r"^([01]\d|2[0-3]):[0-5]\d$")  # 'HH:MM'
    end_time: constr(regex=r"^([01]\d|2[0-3]):[0-5]\d$")    # 'HH:MM'

class AvailabilitySlotCreate(AvailabilitySlotBase):
    pass

class AvailabilitySlotUpdate(BaseModel):
    day_of_week: Optional[conint(ge=0, le=6)] = None
    start_time: Optional[constr(regex=r"^([01]\d|2[0-3]):[0-5]\d$")] = None
    end_time: Optional[constr(regex=r"^([01]\d|2[0-3]):[0-5]\d$")] = None

class AvailabilitySlotResponse(AvailabilitySlotBase):
    id: int

    class Config:
        orm_mode = True 