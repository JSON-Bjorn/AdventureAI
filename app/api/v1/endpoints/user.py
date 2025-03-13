# External imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

# Internal imports
from app.db_setup import get_db
from app.api.v1.validation.schemas import UserCreate, UserUpdate
from app.api.v1.database.operations import DatabaseOperations

router = APIRouter(tags=["users"])


@router.post("/register")
async def register_user(
    user: UserCreate, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Register a new user with email and password"""
    try:
        db_ops = DatabaseOperations(db)
        result = db_ops.create_user(user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {e}"
        )


@router.put("/update")
async def update_user(
    user: UserUpdate, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Update a user's information"""
    pass
