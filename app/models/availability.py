from sqlalchemy import Column, Integer, ForeignKey, String, Time
from sqlalchemy.orm import relationship
from app.models.user import Base

class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(String(5), nullable=False)  # 'HH:MM'
    end_time = Column(String(5), nullable=False)    # 'HH:MM'

    user = relationship("User", backref="availability_slots") 