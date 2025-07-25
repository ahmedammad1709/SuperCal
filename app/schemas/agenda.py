from pydantic import BaseModel, conint, constr
from typing import Optional

class AgendaBase(BaseModel):
    calendar_id: int
    slot_duration: conint(strict=True, ge=30, le=60)
    alias_name: constr(min_length=3, max_length=100)
    is_active: Optional[bool] = True

class AgendaCreate(AgendaBase):
    pass

class AgendaUpdate(BaseModel):
    slot_duration: Optional[conint(strict=True, ge=30, le=60)] = None
    alias_name: Optional[constr(min_length=3, max_length=100)] = None
    is_active: Optional[bool] = None

class AgendaResponse(AgendaBase):
    id: int

    class Config:
        orm_mode = True 