from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.calendar import Calendar
from app.schemas.calendar import CalendarCreate, CalendarUpdate, CalendarResponse
from app.utils import get_db, get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=CalendarResponse)
def create_calendar(calendar: CalendarCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if calendar.is_primary:
        # Unset other primary calendars for this user
        db.query(Calendar).filter(Calendar.user_id == current_user.id, Calendar.is_primary == True).update({Calendar.is_primary: False})
    elif not db.query(Calendar).filter(Calendar.user_id == current_user.id, Calendar.is_primary == True).first():
        # If no primary exists, set this as primary
        calendar.is_primary = True
    db_calendar = Calendar(
        user_id=current_user.id,
        alias=calendar.alias,
        is_primary=calendar.is_primary or False
    )
    db.add(db_calendar)
    db.commit()
    db.refresh(db_calendar)
    return db_calendar

@router.get("/", response_model=List[CalendarResponse])
def list_calendars(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Calendar).filter(Calendar.user_id == current_user.id).all()

@router.put("/{calendar_id}", response_model=CalendarResponse)
def update_calendar(calendar_id: int, update: CalendarUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_calendar = db.query(Calendar).filter(Calendar.id == calendar_id, Calendar.user_id == current_user.id).first()
    if not db_calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")
    if update.is_primary:
        db.query(Calendar).filter(Calendar.user_id == current_user.id, Calendar.is_primary == True).update({Calendar.is_primary: False})
        db_calendar.is_primary = True
    if update.alias:
        db_calendar.alias = update.alias
    db.commit()
    db.refresh(db_calendar)
    return db_calendar 