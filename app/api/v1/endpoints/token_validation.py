"""
File for functionality of endpoints.
"""

from fastapi import HTTPException, Header, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional
from app.api.logger.logger import get_logger
from sqlalchemy.orm import Session
from app.api.v1.database.operations import DatabaseOperations


security = HTTPBearer()
logger = get_logger("app.api.endpoints.token_validation")


def validate_token(token: str, db: Session, get_id: bool = False):
    """Validates the token and optionally returns the user id"""
    logger.info("Validating token")
    user_id = DatabaseOperations(db).validate_token(token)
    if get_id:
        logger.info(f"Token validated, returning user id: {user_id}")
        return user_id
    else:
        logger.info("Token validated")
        return True


def get_token(
    authorization: Optional[str] = Header(),
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """Extracts the token in the request"""
    logger.info("Extracting token from header")
    if authorization is None:
        raise HTTPException(
            status_code=401, detail="Authorization header missing"
        )
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return authorization
