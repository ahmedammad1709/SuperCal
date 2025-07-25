from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from sqlalchemy.orm import scoped_session
import os
import smtplib
from email.mime.text import MIMEText
import datetime
import pytz
from datetime import datetime, timedelta, time as dt_time

DATABASE_URL = "sqlite:///./app.db"
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

RESET_TOKEN_EXPIRE_MINUTES = 15

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    import datetime
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def require_superadmin(current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin privileges required")
    return current_user

# Password reset token

def create_password_reset_token(user_id: int):
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user_id, "exp": expire.timestamp(), "type": "reset"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            raise JWTError()
        return payload.get("sub")
    except JWTError:
        return None

def send_reset_email(background_tasks: BackgroundTasks, to_email: str, reset_link: str):
    def send():
        # Dummy SMTP setup
        msg = MIMEText(f"Click the link to reset your password: {reset_link}")
        msg["Subject"] = "Password Reset"
        msg["From"] = "noreply@example.com"
        msg["To"] = to_email
        try:
            with smtplib.SMTP("localhost", 1025) as server:
                server.sendmail(msg["From"], [to_email], msg.as_string())
        except Exception as e:
            print(f"Email send failed: {e}")
    background_tasks.add_task(send)

def get_todays_meetings(user, date):
    # Stub: Replace with real meeting query
    return [
        {"title": "Meeting 1", "time": "10:00"},
        {"title": "Meeting 2", "time": "15:00"}
    ]

def send_agenda_email(background_tasks: BackgroundTasks, to_email: str, agenda: str):
    def send():
        msg = MIMEText(agenda)
        msg["Subject"] = "Your Daily Agenda"
        msg["From"] = "noreply@example.com"
        msg["To"] = to_email
        try:
            with smtplib.SMTP("localhost", 1025) as server:
                server.sendmail(msg["From"], [to_email], msg.as_string())
        except Exception as e:
            print(f"Agenda email send failed: {e}")
    background_tasks.add_task(send)

def agenda_scheduler(db: Session, background_tasks: BackgroundTasks):
    now_utc = datetime.utcnow()
    users = db.query(User).filter(User.send_daily_agenda == True, User.agenda_send_time != None, User.timezone != None).all()
    for user in users:
        try:
            user_tz = pytz.timezone(user.timezone)
            user_now = now_utc.astimezone(user_tz)
            agenda_time = datetime.strptime(user.agenda_send_time, "%H:%M").time()
            if user_now.time().replace(second=0, microsecond=0) == agenda_time:
                today = user_now.date()
                meetings = get_todays_meetings(user, today)
                agenda = "Your meetings for today:\n" + "\n".join([f"{m['time']} - {m['title']}" for m in meetings])
                send_agenda_email(background_tasks, user.email, agenda)
        except Exception as e:
            print(f"Agenda scheduler error for user {user.id}: {e}")

def sync_secondary_to_primary(db: Session, user: User):
    # Stub: Find all secondary calendars for user
    secondary_cals = db.query(user.calendars.property.mapper.class_).filter_by(user_id=user.id, is_primary=False).all()
    primary_cal = db.query(user.calendars.property.mapper.class_).filter_by(user_id=user.id, is_primary=True).first()
    if not primary_cal:
        print(f"No primary calendar for user {user.id}")
        return
    for cal in secondary_cals:
        # Stub: Get events from secondary calendar
        events = []  # Replace with real fetch
        for event in events:
            # Block as '[Busy]' or clone real title
            title = '[Busy]' if not cal.subject_prefix else f"{cal.subject_prefix} {event['title']}"
            # Insert into primary calendar (stub)
            print(f"Syncing event to primary: {title}")
    print(f"Synced secondary to primary for user {user.id}") 