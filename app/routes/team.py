from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.models.team import Team, TeamMember
from app.models.user import User
from app.models.meeting import Meeting
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.schemas.meeting import MeetingCreate, MeetingResponse
from app.utils import get_db, get_current_user
from app.models.agenda import Agenda
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/", response_model=TeamResponse)
def create_team(team: TeamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_team = Team(user_id=current_user.id, name=team.name)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    for email in team.members:
        db_member = TeamMember(team_id=db_team.id, email=email)
        db.add(db_member)
    db.commit()
    return TeamResponse(id=db_team.id, name=db_team.name, members=team.members)

@router.put("/{team_id}", response_model=TeamResponse)
def update_team(team_id: int, update: TeamUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_team = db.query(Team).filter(Team.id == team_id, Team.user_id == current_user.id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    if update.name:
        db_team.name = update.name
    if update.members is not None:
        db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
        for email in update.members:
            db_member = TeamMember(team_id=team_id, email=email)
            db.add(db_member)
    db.commit()
    members = [m.email for m in db.query(TeamMember).filter(TeamMember.team_id == team_id).all()]
    return TeamResponse(id=db_team.id, name=db_team.name, members=members)

@router.post("/meetings", response_model=List[MeetingResponse])
def create_team_meeting(meeting: MeetingCreate, team_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_team = db.query(Team).filter(Team.id == team_id, Team.user_id == current_user.id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    # Check availability for all members (stub: always available)
    responses = []
    for member in db_team.members:
        is_external = db.query(User).filter(User.email == member.email).first() is None
        db_meeting = Meeting(
            agenda_id=meeting.agenda_id,
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            booked_by_email=member.email,
            meeting_type=meeting.meeting_type,
            travel_time_before=meeting.travel_time_before,
            travel_time_after=meeting.travel_time_after,
            virtual_app=meeting.virtual_app,
            status="booked"
        )
        db.add(db_meeting)
        db.commit()
        db.refresh(db_meeting)
        responses.append(MeetingResponse(
            id=db_meeting.id,
            start_time=db_meeting.start_time,
            end_time=db_meeting.end_time,
            booked_by_email=db_meeting.booked_by_email,
            meeting_type=db_meeting.meeting_type,
            travel_time_before=db_meeting.travel_time_before,
            travel_time_after=db_meeting.travel_time_after,
            virtual_app=db_meeting.virtual_app,
            status=db_meeting.status,
            is_external=is_external
        ))
    return responses 