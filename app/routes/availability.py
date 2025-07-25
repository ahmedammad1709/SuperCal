from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.availability import AvailabilitySlot
from app.schemas.availability import AvailabilitySlotCreate, AvailabilitySlotUpdate, AvailabilitySlotResponse
from app.utils import get_db, get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/slots", response_model=AvailabilitySlotResponse)
def add_slot(slot: AvailabilitySlotCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_slot = AvailabilitySlot(
        user_id=current_user.id,
        day_of_week=slot.day_of_week,
        start_time=slot.start_time,
        end_time=slot.end_time
    )
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

@router.get("/slots", response_model=List[AvailabilitySlotResponse])
def get_my_slots(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(AvailabilitySlot).filter(AvailabilitySlot.user_id == current_user.id).all()

@router.put("/slots/{slot_id}", response_model=AvailabilitySlotResponse)
def update_slot(slot_id: int, slot_update: AvailabilitySlotUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_slot = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == slot_id, AvailabilitySlot.user_id == current_user.id).first()
    if not db_slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    for field, value in slot_update.dict(exclude_unset=True).items():
        setattr(db_slot, field, value)
    db.commit()
    db.refresh(db_slot)
    return db_slot

@router.delete("/slots/{slot_id}", status_code=204)
def delete_slot(slot_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_slot = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == slot_id, AvailabilitySlot.user_id == current_user.id).first()
    if not db_slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    db.delete(db_slot)
    db.commit()
    return None 