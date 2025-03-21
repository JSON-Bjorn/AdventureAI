# External imports
from typing import Dict
from sqlalchemy.orm import Session
import bcrypt
import secrets
import base64
from datetime import datetime, timedelta
import re
import uuid
import sqlalchemy
from fastapi import HTTPException

# Internal imports
from app.api.v1.database.models import Users, Tokens
from app.api.v1.validation.schemas import UserCreate
from sqlalchemy import select
from app.api.logger.logger import (
    get_logger,
)
from app.api.v1.database.models import StartingStories


class DatabaseOperations:
    def __init__(self, db: Session):
        self.db = db
        # Create a class-specific logger as an instance variable
        self.logger = get_logger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )
        self.logger.info("Database operations initialized with session")

    def get_start_story(self, story_id: str):
        """Retrieves a starting story from the database"""
        self.logger.info(f"Retrieving story with ID: {story_id}")

        stmt = select(StartingStories).where(StartingStories.id == story_id)
        result = self.db.execute(stmt)
        story = result.scalar_one_or_none()

        if story is None:
            self.logger.error(f"Story with ID {story_id} not found")
            raise ValueError(f"Story with ID {story_id} not found")
        return story

    def save_game(self, context: Dict):
        # Post game save to db
        self.logger.info(
            f"Saving game with context: {context.get('game_id', 'unknown')}"
        )
        pass

    def load_game(self, game_id: str):
        # Get the game sve from db
        self.logger.info(f"Loading game with ID: {game_id}")
        pass

    def validate_token(self, token: str) -> Dict:
        """Validate a token and return user info if valid"""
        self.logger.info("Validating user token")
        db_token = self.db.query(Tokens).filter(Tokens.token == token).first()

        if not db_token:
            return {"valid": False, "error": "Token not found"}

        current_time = datetime.now()

        if db_token.expires_at < current_time:
            return {"valid": False, "error": "Token expired"}

        return {"valid": True, "user_id": db_token.user_id}

    def create_user(self, user_data: UserCreate) -> Dict:
        """Create a new user in the database"""
        self.logger.info(f"Creating new user with email: {user_data.email}")
        # Validate email format
        if not self._validate_email(user_data.email):
            raise HTTPException(
                status_code=400,
                detail="Invalid email format",
            )

        # Check if user already exists
        if self._check_existing_user(user_data.email):
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists",
            )

        # Hash the password
        password_bytes = user_data.password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        hashed_password_str = hashed_password.decode("utf-8")

        # Create the user
        for attempt in range(3):
            try:
                db_user = Users(
                    id=uuid.uuid4(),
                    email=user_data.email,
                    password=hashed_password_str,
                )
                break
            except sqlalchemy.exc.IntegrityError:
                self.logger.error(
                    "Error posting to Users table due to UUID unique constraint. "
                    "If this happened, reality is a simulation."
                )
                if attempt == 2:
                    raise HTTPException(
                        status_code=500,
                        detail="User creation failed when posting to database.",
                    )
                continue
        # Add the user to the database
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        # Get access token
        access_token = self._create_access_token(db_user.id)

        return {"access_token": access_token}

    def _create_access_token(self, user_id: int) -> str:
        """Create an access token for the user"""
        self.logger.debug(f"Creating access token for user ID: {user_id}")
        # Generate a secure random token
        token_bytes = secrets.token_bytes(32)

        # Convert to base64 for string representation
        token_base64 = base64.urlsafe_b64encode(token_bytes)
        token = token_base64.decode("utf-8")
        token = token.rstrip("=")

        # Set the expiration time (e.g., 1 hour from now)
        current_time = datetime.now()
        expires_at = current_time + timedelta(hours=1)

        # Create token record
        db_token = Tokens(token=token, expires_at=expires_at, user_id=user_id)

        # Store the token in the database
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)

        return token

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        self.logger.debug(f"Validating email format: {email}")
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        is_valid = re.match(email_pattern, email)
        return bool(is_valid)

    def _check_existing_user(self, email: str) -> bool:
        """Check if a user with the given email already exists"""
        self.logger.debug(f"Checking if user exists with email: {email}")
        existing_user = (
            self.db.query(Users).filter(Users.email == email).first()
        )

        return bool(existing_user)
