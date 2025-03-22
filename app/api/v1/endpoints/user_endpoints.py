# External imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

# Internal imports
from app.db_setup import get_db
from app.api.v1.database.operations import DatabaseOperations
from app.api.v1.endpoints.token_validation import get_token, validate_token
from app.api.logger.logger import get_logger
from app.api.v1.validation.schemas import (
    UserCreate,
    UserUpdate,
    UserLogin,
    UserEmail,
)


logger = get_logger("app.api.endpoints.user")

router = APIRouter(tags=["users"])


@router.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with email and password"""
    logger.info(f"Register User endpoint requested with email: {user.email}")
    db_ops = DatabaseOperations(db)
    result = db_ops.create_user(user)
    logger.info(f"Successfully registered user with email: {user.email}")
    return result


@router.put("/update")
async def update_user(
    user: UserUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
):
    """Update a user's information"""
    logger.info(f"Updating user information for user ID: {user.id}")
    pass


@router.post("/login")
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """Login a user with email and password"""
    logger.info(
        f"Login User endpoint requested with email: {str(user.email)[:5]}..."
    )
    token = DatabaseOperations(db).login_user(user)
    return {"token": token}


@router.delete("/logout")
async def logout_user(
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
) -> Dict[str, str]:
    """Logout a user"""
    logger.info(f"Logout User endpoint requested with token: {token[:10]}...")
    user_id = validate_token(token, db, get_id=True)
    DatabaseOperations(db).logout_user(user_id)
    return {"message": "User logged out successfully"}
