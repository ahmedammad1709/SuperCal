from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.user import Base

class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(Integer, primary_key=True, index=True)
    agenda_id = Column(Integer, ForeignKey("agendas.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    booked_by_email = Column(String(120), nullable=False)
    meeting_type = Column(String(20), nullable=False)  # "virtual" or "in-person"
    travel_time_before = Column(Integer, default=0, nullable=True)  # minutes
    travel_time_after = Column(Integer, default=0, nullable=True)   # minutes
    virtual_app = Column(String(50), nullable=True)  # e.g., Zoom, Jitsi
    status = Column(String(20), default="booked", nullable=False)

    agenda = relationship("Agenda", backref="meetings") 