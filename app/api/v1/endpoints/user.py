# External imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

# Internal imports
from app.db_setup import get_db
from app.api.v1.validation.schemas import UserCreate, UserUpdate
from app.api.v1.database.operations import DatabaseOperations
from app.api.logger.logger import get_logger

logger = get_logger("app.api.endpoints.user")

router = APIRouter(tags=["users"])


@router.post("/register")
async def register_user(
    user: UserCreate, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Register a new user with email and password"""
    logger.info(f"Register User endpoint requested with email: {user.email}")
    try:
        db_ops = DatabaseOperations(db)
        result = db_ops.create_user(user)
        logger.info(f"Successfully registered user with email: {user.email}")
        return result
    except ValueError as e:
        logger.warning(f"Registration failed for {user.email}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal error during user registration: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {e}"
        )


@router.put("/update")
async def update_user(
    user: UserUpdate, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Update a user's information"""
    logger.info(f"Updating user information for user ID: {user.id}")
    try:
        # Do the thing here aswell
        logger.warning("User update functionality not implemented yet")
        return {"message": "User update not implemented yet"}
    except ValueError as e:
        logger.warning(f"User update failed for ID {user.id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal error during user update: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {e}"
        )
