from pydantic import BaseModel, EmailStr
from typing import List, Optional

class TeamMemberBase(BaseModel):
    email: EmailStr

class TeamMemberResponse(TeamMemberBase):
    id: int
    class Config:
        orm_mode = True

class TeamBase(BaseModel):
    name: str
    members: List[EmailStr]

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    members: Optional[List[EmailStr]] = None

class TeamResponse(TeamBase):
    id: int
    members: List[EmailStr]
    class Config:
        orm_mode = True 