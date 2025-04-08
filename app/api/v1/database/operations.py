"""
Class for all database operations.
Methods within DatabaseOperations are currently sorted after which class they will be moved into.

The plan is to have 3 new classes:
- UserManager
- TokenManager
- GameManager
Let these classes inherit from DatbaseOperations and mvoe all methods to the new classes.

After moving everything we need to change every import and every line that uses DatabaseOperations.
We also need to change the way we call other methods within this class if they are separated into two different classes.
"""

# External imports
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import Dict, List, Any
from uuid import UUID
from datetime import datetime, timedelta
import re
import uuid
import bcrypt
import secrets
import base64

# Internal imports
from app.api.logger.loggable import Loggable

from app.api.v1.database.models import (
    Users,
    Tokens,
    StartingStories,
    GameSessions,
    EmailTokens,
)
from app.api.v1.validation.schemas import (
    UserCreate,
    SaveGame,
    UserLogin,
    UserUpdate,
)


class DatabaseOperations(Loggable):
    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.logger.info("Database operations initialized with session")

    """
    USER MANAGER
    """

    def create_user(self, token: str) -> Dict:
        """Creates a new row in the users table with information taken from email_token table."""
        user_data = self._validate_email_token(token)
        self.logger.info(f"Creating new user: {user_data.email[:10]}...")
        for attempt in range(3):
            try:
                db_user = Users(
                    id=uuid.uuid4(),
                    email=user_data.email,
                    password=user_data.password,
                )
                self.db.add(db_user)
                self.db.commit()
                self.db.refresh(db_user)
                break
            except IntegrityError:
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
        access_token = self._create_access_token(db_user.id)
        return {"access_token": access_token}

    def login_user(self, user: UserLogin):
        """Logs in a user by creating a new authorization token. Activates a user if they are not active."""
        self.logger.info(f"Logging in user: {user.email[:10]}...")
        stmt = select(Users).where(Users.email == user.email)
        result = self.db.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if not bcrypt.checkpw(
            user.password.encode("utf-8"), db_user.password.encode("utf-8")
        ):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if db_user.is_active is False:
            self.activate_user(db_user.id)
        token = self._create_access_token(user_id=db_user.id)
        return token

    def logout_user(self, user_id: UUID):
        """Logout a user by deleting their active tokens"""
        stmt = delete(Tokens).where(Tokens.user_id == user_id)
        self.db.execute(stmt)
        self.db.commit()
        self.logger.info(f"Removed all tokens for user ID: {str(user_id)[:10]}...")

    def update_user(self, user_id: UUID, user: UserUpdate):
        """Updates a user in the database"""
        nud = {}  # New-User-Data
        for key, value in user.model_dump().items():
            if value is not None:
                nud[key] = value
        if "password" in nud:
            nud["password"] = self._hash_password(nud["password"])
        stmt = update(Users).where(Users.id == user_id).values(**nud).returning(Users)
        result = self.db.execute(stmt)
        updated_user = result.scalar_one_or_none()
        self.db.commit()
        if updated_user:
            return updated_user
        else:
            self.logger.critical(
                f"Token for user ID: {user_id} passed authorization check "
                "but the user_id does not exist in the database.\n"
                "Removing all tokens for this user.."
            )
            self.logout_user(user_id)
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

    def activate_user(self, user_id: UUID):
        """Activate a user by setting is_active to True"""
        stmt = (
            update(Users)
            .where(Users.id == user_id)
            .values(is_active=True)
            .returning(Users)
        )
        result = self.db.execute(stmt)
        updated_user = result.scalar_one_or_none()
        self.db.commit()
        if updated_user is None:
            self.logger.critical(
                f"Token for user ID: {user_id} passed authorization check "
                "but the user_id does not exist in the database.\n"
                "Removing all tokens for this user.."
            )
            self.logout_user(user_id)
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

    def deactivate_user(self, user_id: UUID):
        """Deactivates a user by changing their is_active-column to False"""
        self.logout_user(user_id)
        stmt = (
            update(Users)
            .where(Users.id == user_id)
            .values(is_active=False)
            .returning(Users)
        )
        result = self.db.execute(stmt)
        updated_user = result.scalar_one_or_none()
        self.db.commit()
        if updated_user is None:
            self.logger.critical(
                f"A token tied to user ID: {user_id} successfully "
                "authenticated access to a protected endpoint (/soft_delete_user). "
                "But the user with this ID does not exist in the database. "
            )
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

    def hard_delete_user(self, user_id: UUID):
        """Hard deletes a user by removing their row from the database"""
        get_stmt = select(Users).where(Users.id == user_id)
        result = self.db.execute(get_stmt)
        user = result.scalar_one_or_none()
        email = user.email

        self.logout_user(user_id)
        delete_stmt = delete(Users).where(Users.id == user_id)
        result = self.db.execute(delete_stmt)
        if result.rowcount == 0:
            self.logger.critical(
                f"A token tied to user ID: {user_id} successfully "
                "authenticated access to a protected endpoint (/hard_delete_user). "
                "But the user with this ID does not exist in the database. "
            )
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )
        else:
            self.db.commit()
            self.logger.info(f"Successfully deleted user ID: {str(user_id)[:10]}...")
        self._delete_email_tokens(email)
        return {"message": "User deleted successfully"}

    def _validate_email(self, email: str) -> bool:
        """Validates email format"""
        self.logger.debug(f"Validating email format: {email[:5]}...")
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        is_valid = re.match(email_pattern, email)
        return bool(is_valid)

    def _check_existing_user(self, email: str) -> bool:
        """Checks if a user with the given email already exists"""
        self.logger.debug(f"Checking if email: {email[:5]} exists...")
        stmt = select(Users).where(Users.email == email)
        result = self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        return bool(existing_user)

    """
    TOKEN MANAGER
    """

    def generate_token(self) -> str:
        token_bytes = secrets.token_bytes(32)
        token_base64 = base64.urlsafe_b64encode(token_bytes)
        token = token_base64.decode("utf-8")
        token = token.rstrip("=")
        return token

    def _create_access_token(self, user_id: UUID) -> str:
        """Generates a new authorization token for a user and deletes all their previous tokens"""
        self.logger.debug(f"Creating access token for user ID: {str(user_id)[:10]}...")
        self.logout_user(user_id)
        token = self.generate_token()
        current_time = datetime.now()
        expires_at = current_time + timedelta(hours=720)  # 30 days
        db_token = Tokens(token=token, expires_at=expires_at, user_id=user_id)
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return token

    def validate_token(self, token: str) -> UUID:
        """Validates an authorization token and returns the user_id"""
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
            self.logger.info(f"Token validated for user: {str(user_id)[:10]}...")
            return user_id

    def create_email_token(self, user: UserCreate) -> str:
        """Generates new token and creates a row in the EmailTokens table"""
        if not self._validate_email(user.email):
            raise HTTPException(
                status_code=400,
                detail="Invalid email format",
            )
        if self._check_existing_user(user.email):
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists",
            )

        try:
            token = self._post_email_token(user)
        except IntegrityError:
            # If the user never clicked the activation
            self._delete_email_tokens(email=user.email)
            token = self._post_email_token(user)

        return token

    def _post_email_token(self, user: UserCreate) -> str:
        """Creates a new email-token row for a user"""
        hashed_pw = self._hash_password(user.password)
        token = self.generate_token()
        stmt = insert(EmailTokens).values(
            email=user.email,
            password=hashed_pw,
            token=token,
        )
        self.db.execute(stmt)
        self.db.commit()

        return token

    def _delete_email_tokens(self, email: str):
        stmt = delete(EmailTokens).where(EmailTokens.email == email)
        self.db.execute(stmt)
        self.db.commit()

    def _validate_email_token(self, token: str) -> Users:
        """Checks if an email exists in databaseand returns the database object"""
        stmt = select(EmailTokens).where(EmailTokens.token == token)
        result = self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Token not found")
        if user.created_at + timedelta(minutes=60) < datetime.now():
            self._delete_email_tokens(user.email)
            raise HTTPException(status_code=401, detail="Token expired")
        return user

    def update_email_token(self, email: str) -> str:
        """Generates and changes the email token for a user"""
        self.logger.info(f"Updating email token for user: {email[:5]}...")
        stmt = select(EmailTokens).where(EmailTokens.email == email)
        result = self.db.execute(stmt)
        token_data = result.scalar_one_or_none()
        if not token_data:
            raise HTTPException(status_code=404, detail="Email not registered")
        new_token = self.generate_token()
        stmt = (
            update(EmailTokens)
            .where(EmailTokens.email == email)
            .values(
                token=new_token,
                created_at=datetime.now(),
            )
        )
        self.db.execute(stmt)
        self.db.commit()
        return new_token

    def reset_password(self, token: str, password: str):
        """Changes a user's password via reset link"""
        user_data = self._validate_email_token(token)
        hashed_pw = self._hash_password(password)
        stmt = (
            update(Users)
            .where(Users.email == user_data.email)
            .values(password=hashed_pw)
        )
        self.db.execute(stmt)
        self.db.commit()
        self.update_email_token(user_data.email)  # Makes link a one-time use
        return user_data

    def _hash_password(self, password: str) -> str:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        hashed_password_str = hashed_password.decode("utf-8")
        return hashed_password_str

    """
    GAME MANAGER
    """

    def get_start_story(self, story_id: str):
        """Gets a starting story from the database"""
        self.logger.info(f"Getting story with ID: {story_id}")

        stmt = select(StartingStories).where(StartingStories.id == story_id)
        result = self.db.execute(stmt)
        starting_story = result.scalar_one_or_none()

        if starting_story.story is None or starting_story.image is None:
            self.logger.error(f"Story with ID {story_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Story with ID {story_id} not found",
            )
        return {
            "image": starting_story.image,
            "story": starting_story.story,
            "id": starting_story.id,
        }

    def load_game(self, user_id: str):
        """Gets all game sessions from a user"""
        stmt = select(GameSessions).where(GameSessions.user_id == user_id)
        result = self.db.execute(stmt)
        all_saves: List[GameSessions] = result.scalars().all()
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
                    "last_played": save.updated_at,
                }
            )
        return response_data

    def get_user_profile(self, user_id: UUID) -> Dict[str, Any]:
        """Gets a user's profile information"""
        stmt = select(Users).where(Users.id == user_id)
        result = self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        created_date = user.created_at.strftime("%Y-%m-%d") if user.created_at else None

        return {
            "email": user.email,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "registered_at": created_date,
        }

    def save_game_route(self, data: SaveGame, user_id):
        """Saves a game session."""
        # Saving to a new row
        if data.game_session.id is None:
            stmt = (
                insert(GameSessions)
                .values(
                    user_id=user_id,
                    last_image=data.image,
                    protagonist_name=data.game_session.protagonist_name,
                    session_name=data.game_session.session_name,
                    inventory=data.game_session.inventory,
                    stories=data.game_session.scenes,
                )
                .returning(GameSessions.id)
            )
            result = self.db.execute(stmt)
            game_id = result.scalar_one()

        # Saving to an existing row
        else:
            existing_stmt = select(GameSessions.stories).where(
                GameSessions.id == data.game_session.id
            )
            result = self.db.execute(existing_stmt)
            old_scenes = result.scalar_one_or_none()
            updated_scenes = old_scenes + data.game_session.scenes
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
            game_id = data.game_session.id

        self.db.commit()

        return game_id
