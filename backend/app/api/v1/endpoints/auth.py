from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_session
from app.db.base import UserProfile
from app.schemas import UserCreate, UserResponse
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, session: Session = Depends(get_session)):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = session.query(UserProfile).filter(
        UserProfile.email == user.email
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    db_user = UserProfile(
        user_id=user.user_id,
        email=user.email,
        display_name=user.display_name,
        role=user.role or "patient"
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: str, session: Session = Depends(get_session)):
    """Get current user profile"""
    
    user = session.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.put("/profile", response_model=UserResponse)
async def update_profile(user_id: str, updates: dict, session: Session = Depends(get_session)):
    """Update user profile"""
    
    user = session.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in updates.items():
        if hasattr(user, key) and key != "user_id":
            setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(user)
    
    return user
