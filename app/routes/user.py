from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate, UserCreateByAdmin
from app.models.user import User
from app.utils import get_db, create_access_token, get_password_hash, verify_password, get_current_user, require_superadmin, send_reset_email, create_password_reset_token, verify_password_reset_token
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.alias == user.alias).first():
        raise HTTPException(status_code=400, detail="Alias already taken")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        alias=user.alias,
        image_url=user.image_url,
        description=user.description,
        role="user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token({"sub": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- Superadmin Endpoints ---

@router.post("/admin/create_user", response_model=UserResponse)
def create_user_by_admin(user: UserCreateByAdmin, db: Session = Depends(get_db), current_user: User = Depends(require_superadmin)):
    if user.role not in ["user", "superadmin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.alias == user.alias).first():
        raise HTTPException(status_code=400, detail="Alias already taken")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        alias=user.alias,
        image_url=user.image_url,
        description=user.description,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/admin/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_superadmin)):
    return db.query(User).all()

@router.put("/admin/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_superadmin)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.email and db.query(User).filter(User.email == user_update.email, User.id != user_id).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if user_update.alias and db.query(User).filter(User.alias == user_update.alias, User.id != user_id).first():
        raise HTTPException(status_code=400, detail="Alias already taken")
    for field, value in user_update.dict(exclude_unset=True).items():
        if field != "password":
            setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user 

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@router.post("/password-reset-request")
def password_reset_request(data: PasswordResetRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), request: Request = None):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"message": "If the email exists, a reset link will be sent."}
    token = create_password_reset_token(user.id)
    base_url = str(request.base_url) if request else "http://localhost:8000/"
    reset_link = f"{base_url}users/password-reset?token={token}"
    send_reset_email(background_tasks, user.email, reset_link)
    return {"message": "If the email exists, a reset link will be sent."}

@router.post("/password-reset")
def password_reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    user_id = verify_password_reset_token(data.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password reset successful"} 

class OAuth2TokenRequest(BaseModel):
    provider: str
    refresh_token: str
    access_token: str
    token_expiry: datetime

@router.patch("/oauth2-token")
def store_oauth2_token(data: OAuth2TokenRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.provider = data.provider
    current_user.refresh_token = data.refresh_token
    current_user.access_token = data.access_token
    current_user.token_expiry = data.token_expiry
    db.commit()
    db.refresh(current_user)
    return {"message": "OAuth2 tokens updated"} 