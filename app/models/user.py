from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    alias = Column(String(50), unique=True, index=True, nullable=False)
    image_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    role = Column(String(20), nullable=False, default="user")
    send_daily_agenda = Column(Boolean, default=False, nullable=False)
    agenda_send_time = Column(String(5), nullable=True)  # 'HH:MM'
    timezone = Column(String(64), nullable=True)
    provider = Column(String(20), nullable=True)  # 'google', 'outlook', etc.
    refresh_token = Column(Text, nullable=True)
    access_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=True) 