from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.user import Base

class Calendar(Base):
    __tablename__ = "calendars"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    alias = Column(String(100), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    sync_direction = Column(String(10), default="one-way", nullable=False)  # 'one-way' or 'two-way'
    subject_prefix = Column(String(50), nullable=True)

    user = relationship("User", backref="calendars") 