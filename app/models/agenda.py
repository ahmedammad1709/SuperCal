from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.user import Base

class Agenda(Base):
    __tablename__ = "agendas"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    calendar_id = Column(Integer, ForeignKey("calendars.id"), nullable=False)
    slot_duration = Column(Integer, nullable=False)  # 30, 45, 60
    alias_name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", backref="agendas")
    calendar = relationship("Calendar", backref="agendas") 