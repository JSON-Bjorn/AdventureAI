# External imports
from typing import Dict
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

# Internal imports
from app.db_setup import get_db
from app.api.logger.logger import get_logger
from app.api.v1.database.operations import DatabaseOperations
from app.api.v1.endpoints.token_validation import get_token, requires_auth
from app.api.v1.endpoints.rate_limiting import rate_limit
from app.api.v1.validation.schemas import (
    UserCreate,
    UserUpdate,
    UserLogin,
)


logger = get_logger("app.api.endpoints.user")
router = APIRouter(tags=["users"])


@router.post("/register")
@rate_limit(authenticated_limit=6, unauthenticated_limit=6)
async def register_user(
    request: Request, user: UserCreate, db: Session = Depends(get_db)
):
    """Register a new user with email and password"""
    logger.info(f"Registering new user with email: {str(user.email)[:5]}...")
    db_ops = DatabaseOperations(db)
    result = db_ops.create_user(user)
    logger.info(
        f"Successfully registered user with email: {str(user.email)[:5]}..."
    )
    return result


@router.post("/login")
@rate_limit(authenticated_limit=6, unauthenticated_limit=6)
async def login_user(
    request: Request, user: UserLogin, db: Session = Depends(get_db)
):
    """Login a user with email and password"""
    logger.info(
        f"Login User endpoint requested with email: {str(user.email)[:5]}..."
    )
    token = DatabaseOperations(db).login_user(user)
    logger.info(
        f"Successfully logged in user with email: {user.email[:5]}... "
        "Returning token to client."
    )
    return {"token": token}


@router.put("/update")
@requires_auth(get_id=True)
@rate_limit(authenticated_limit=10, unauthenticated_limit=10)
async def update_user(
    request: Request,
    user: UserUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    user_id: int = None,
):
    """Update a user's information"""
    logger.info(
        f"Updating user information for user ID: {str(user_id)[:5]}..."
    )
    DatabaseOperations(db).update_user(user_id, user)
    logger.info(
        f"Successfully updated user information for user ID: {str(user_id)[:5]}..."
    )
    return {"message": "User information updated successfully"}


@router.delete("/logout")
@requires_auth(get_id=True)
@rate_limit(authenticated_limit=6, unauthenticated_limit=6)
async def logout_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    user_id: int = None,
) -> Dict[str, str]:
    """Logout a user"""
    logger.info(f"Logging out user ID: {str(user_id)[:5]}...")
    DatabaseOperations(db).logout_user(user_id)
    return {"message": "User logged out successfully"}


@router.put("/soft_delete_user")
@requires_auth(get_id=True)
@rate_limit(authenticated_limit=1, unauthenticated_limit=1)
async def soft_delete_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    user_id: int = None,
) -> Dict[str, str]:
    """Marks a user as inactive in the database"""
    logger.info(f"Deactivating user ID: {str(user_id)[:5]}...")
    DatabaseOperations(db).deactivate_user(user_id)
    return {"message": "User deactivated successfully"}


@router.put("/activate_user")
@requires_auth(get_id=True)
@rate_limit(authenticated_limit=1, unauthenticated_limit=1)
async def activate_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    user_id: int = None,
) -> Dict[str, str]:
    """Reactivates a user in the database"""
    logger.info(f"Reactivating user ID: {str(user_id)[:5]}...")
    DatabaseOperations(db).activate_user(user_id)
    return {"message": "User reactivated successfully"}


@router.delete("/hard_delete_user")
@requires_auth(get_id=True)
@rate_limit(authenticated_limit=1, unauthenticated_limit=1)
async def hard_delete_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(get_token),
    user_id: int = None,
) -> Dict[str, str]:
    """Deletes the users row in the database"""
    logger.info(f"Deleting user ID: {str(user_id)[:5]}...")
    DatabaseOperations(db).hard_delete_user(user_id)
    return {"message": "User deleted successfully"}
