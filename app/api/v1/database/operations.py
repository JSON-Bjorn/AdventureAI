# External imports
from typing import Dict, List
from uuid import UUID
from sqlalchemy.orm import Session
import bcrypt
import secrets
import base64
from datetime import datetime, timedelta
import re
import uuid
import sqlalchemy
from sqlalchemy import select, insert, update, func, text
from fastapi import HTTPException

# Internal imports
from app.api.v1.database.models import (
    Users,
    Tokens,
    StartingStories,
    GameSessions,
)
from app.api.v1.validation.schemas import UserCreate, SaveGame, GameSession
from app.api.logger.loggable import Loggable


class DatabaseOperations(Loggable):
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.logger.info("Database operations initialized with session")

    def validate_token(self, token: str) -> UUID:
        """Validate a token and return the user_id if valid"""
        self.logger.info(f"Validating user token: {token[:10]}...")

        stmt = select(Tokens).where(Tokens.token == token)
        result = self.db.execute(stmt)
        token_data = result.scalar_one_or_none()

        if not token_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )
        else:
            user_id = token_data.user_id
            self.logger.info(
                f"Token validated for user: {str(user_id)[:10]}..."
            )
            return user_id

    def save_game_route(self, data: SaveGame, user_id):
        """Routes incoming save-requests to the correct method"""
        if data.game_session.id is None:
            self._save_new_game(data, user_id)
        else:
            self._save_old_game(data, user_id)

    def _save_new_game(self, data: SaveGame, user_id):
        """Saves entire new game sessions to the database"""
        # Extract the game session data for easy access
        stmt = insert(GameSessions).values(
            user_id=user_id,
            last_image=data.image,
            protagonist_name=data.game_session.protagonist_name,
            session_name=data.game_session.session_name,
            inventory=data.game_session.inventory,
            stories=data.game_session.scenes,
        )
        self.db.execute(stmt)
        self.db.commit()

    def _save_old_game(self, data: SaveGame, user_id):
        """Saves scenes to an already existing game session"""
        # Get the current stories from db row
        stmt = select(GameSessions.stories).where(
            GameSessions.id == data.game_session.id
        )
        result = self.db.execute(stmt)
        old_scenes = result.scalar_one_or_none()

        # Combine the two lists
        updated_scenes = old_scenes + data.game_session.scenes

        # Build the query for post
        stmt = (
            update(GameSessions)
            .where(GameSessions.id == data.game_session.id)
            .values(
                last_image=data.image,
                session_name=data.game_session.session_name,
                inventory=data.game_session.inventory,
                stories=updated_scenes,
            )
        )
        self.db.execute(stmt)
        self.db.commit()

    def load_game(self, user_id: str):
        """Loads all game sessions from a user"""
        # Get the game saves from database
        stmt = select(GameSessions).where(GameSessions.user_id == user_id)
        result = self.db.execute(stmt)
        all_saves: List[GameSessions] = result.scalars().all()

        # Convert and return the saves as readable data
        response_data = []
        for save in all_saves:
            response_data.append(
                {
                    "id": save.id,
                    "protagonist_name": save.protagonist_name,
                    "inventory": save.inventory,
                    "session_name": save.session_name,
                    "stories": save.stories,
                    "image": save.last_image,
                }
            )
        return response_data

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

        # Create and post user to db
        for attempt in range(3):
            try:
                db_user = Users(
                    id=uuid.uuid4(),
                    email=user_data.email,
                    password=hashed_password_str,
                )
                self.db.add(db_user)
                self.db.commit()
                self.db.refresh(db_user)
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
