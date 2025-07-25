from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List
from app.models.agenda import Agenda
from app.models.meeting import Meeting
from app.schemas.agenda import AgendaCreate, AgendaUpdate, AgendaResponse
from app.schemas.meeting import MeetingCreate, MeetingResponse
from app.utils import get_db, get_current_user, send_reset_email
from app.models.user import User
from datetime import datetime, timedelta
import os

router = APIRouter()

# Configurable max bookings per visitor per agenda (could be a user field, here as constant for demo)
MAX_BOOKINGS_PER_VISITOR = 3

@router.post("/", response_model=AgendaResponse)
def create_agenda(agenda: AgendaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if db.query(Agenda).filter(Agenda.alias_name == agenda.alias_name).first():
        raise HTTPException(status_code=400, detail="Alias name already taken")
    db_agenda = Agenda(
        user_id=current_user.id,
        calendar_id=agenda.calendar_id,
        slot_duration=agenda.slot_duration,
        alias_name=agenda.alias_name,
        is_active=agenda.is_active if agenda.is_active is not None else True
    )
    db.add(db_agenda)
    db.commit()
    db.refresh(db_agenda)
    return db_agenda

@router.get("/", response_model=List[AgendaResponse])
def list_agendas(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Agenda).filter(Agenda.user_id == current_user.id).all()

@router.get("/public/{alias_name}", response_model=AgendaResponse)
def get_public_agenda(alias_name: str, db: Session = Depends(get_db)):
    agenda = db.query(Agenda).filter(Agenda.alias_name == alias_name, Agenda.is_active == True).first()
    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda not found")
    return agenda

@router.get("/public/{alias_name}/slots")
def get_available_slots(alias_name: str, db: Session = Depends(get_db)):
    # Stub: Return next 7 days, 9am-5pm, slot_duration from agenda
    agenda = db.query(Agenda).filter(Agenda.alias_name == alias_name, Agenda.is_active == True).first()
    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda not found")
    now = datetime.utcnow()
    slots = []
    for day in range(7):
        date = now + timedelta(days=day)
        start = datetime(date.year, date.month, date.day, 9, 0)
        end = datetime(date.year, date.month, date.day, 17, 0)
        slot = start
        while slot + timedelta(minutes=agenda.slot_duration) <= end:
            slot_end = slot + timedelta(minutes=agenda.slot_duration)
            # Check for conflicts
            conflict = db.query(Meeting).filter(Meeting.agenda_id == agenda.id, Meeting.start_time < slot_end, Meeting.end_time > slot).first()
            if not conflict:
                slots.append({"start_time": slot, "end_time": slot_end})
            slot = slot_end
    return slots

@router.post("/public/{alias_name}/book", response_model=MeetingResponse)
def book_meeting(alias_name: str, meeting: MeetingCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), request: Request = None):
    agenda = db.query(Agenda).filter(Agenda.alias_name == alias_name, Agenda.is_active == True).first()
    if not agenda:
        raise HTTPException(status_code=404, detail="Agenda not found")
    # Enforce max bookings per visitor
    count = db.query(Meeting).filter(Meeting.agenda_id == agenda.id, Meeting.visitor_email == meeting.visitor_email).count()
    if count >= MAX_BOOKINGS_PER_VISITOR:
        raise HTTPException(status_code=400, detail="Booking limit reached for this agenda")
    # Check for slot conflict
    conflict = db.query(Meeting).filter(Meeting.agenda_id == agenda.id, Meeting.start_time < meeting.end_time, Meeting.end_time > meeting.start_time).first()
    if conflict:
        raise HTTPException(status_code=400, detail="Slot already booked")
    db_meeting = Meeting(
        agenda_id=agenda.id,
        visitor_email=meeting.visitor_email,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        status="booked"
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    # Send confirmation email (reuse send_reset_email for demo)
    base_url = str(request.base_url) if request else "http://localhost:8000/"
    msg = f"Your meeting is booked for {meeting.start_time} - {meeting.end_time} on {base_url}smartcal.one/{alias_name}"
    send_reset_email(background_tasks, meeting.visitor_email, msg)
    return db_meeting 