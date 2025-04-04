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

    def create_email_token(self, user: UserCreate) -> Dict:
        """Creates a email token in the database"""
        self.logger.info(f"Creating email token for user: {user.email}")
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

    def update_email_token(self, email: str) -> str:
        """Updates the email token in the database when a user requests a password reset"""
        self.logger.info(f"Updating email token for user: {email}")

        stmt = select(EmailTokens).where(EmailTokens.email == email)
        result = self.db.execute(stmt)
        token_data = result.scalar_one_or_none()

        if not token_data:
            raise HTTPException(
                status_code=404, detail="Email not registered"
            )

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

    def generate_token(self) -> str:
        token_bytes = secrets.token_bytes(32)
        token_base64 = base64.urlsafe_b64encode(token_bytes)
        token = token_base64.decode("utf-8")
        token = token.rstrip("=")
        return token

    def _validate_email_token(self, token: str) -> Users:
        """Checks if an email exists in databaseand returns the database object"""
        stmt = select(EmailTokens).where(EmailTokens.token == token)
        result = self.db.execute(stmt)
        user_data = result.scalar_one_or_none()

        if not user_data:
            raise HTTPException(status_code=404, detail="Token not found")

        if user_data.created_at + timedelta(minutes=60) < datetime.now():
            raise HTTPException(status_code=401, detail="Token expired")

        return user_data

    def create_user(self, token: str) -> Dict:
        """Create a new user in the database"""
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

        stmt = delete(EmailTokens).where(EmailTokens.token == token)
        self.db.execute(stmt)
        self.db.commit()

        access_token = self._create_access_token(db_user.id)
        return {"access_token": access_token}

    def login_user(self, user: UserLogin):
        """Login a user with email and password"""
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
        self.logger.info(
            f"Removed all tokens for user ID: {str(user_id)[:10]}..."
        )

    def update_user(self, user_id: UUID, user: UserUpdate):
        """Updates a user in the db"""
        nud = {}  # New-User-Data
        for key, value in user.model_dump().items():
            if value is not None:
                nud[key] = value

        if "password" in nud:
            nud["password"] = self._hash_password(nud["password"])

        stmt = (
            update(Users)
            .where(Users.id == user_id)
            .values(**nud)
            .returning(Users)
        )
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
        """Deactivate a user by setting is_active to False"""
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
        """Hard delete a user by deleting their row from the database"""
        self.logout_user(user_id)

        stmt = delete(Users).where(Users.id == user_id)
        result = self.db.execute(stmt)

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
            self.logger.info(
                f"Successfully deleted user ID: {str(user_id)[:10]}..."
            )
            return {"message": "User deleted successfully"}

    def save_game_route(self, data: SaveGame, user_id):
        """Routes incoming save-requests to the correct method"""
        if data.game_session.id is None:
            game_id = self._save_new_game(data, user_id)
        else:
            game_id = self._save_old_game(data, user_id)
        return game_id

    def _save_new_game(self, data: SaveGame, user_id):
        """Saves entire new game sessions to the database"""
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
        self.db.commit()

        return game_id

    def get_start_story(self, story_id: str):
        """Retrieves a starting story from the database"""
        self.logger.info(f"Retrieving story with ID: {story_id}")

        stmt = select(StartingStories).where(StartingStories.id == story_id)
        result = self.db.execute(stmt)
        starting_story = result.scalar_one_or_none()

        image = starting_story.image
        story = starting_story.story
        id = starting_story.id

        response = {
            "image": image,
            "story": story,
            "id": id,
        }

        if story is None or image is None:
            self.logger.error(f"Story with ID {story_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"Story with ID {story_id} not found",
            )
        return response

    def load_game(self, user_id: str):
        """Loads all game sessions from a user"""
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

    def _save_old_game(self, data: SaveGame, user_id):
        """Saves scenes to an already existing game session"""
        stmt = select(GameSessions.stories).where(
            GameSessions.id == data.game_session.id
        )
        result = self.db.execute(stmt)
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
        self.db.commit()

        game_id = data.game_session.id
        return game_id

    def _hash_password(self, password: str) -> str:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        hashed_password_str = hashed_password.decode("utf-8")
        return hashed_password_str

    def _create_access_token(self, user_id: UUID) -> str:
        """Create an access token in the database and deletes all their previous tokens"""
        self.logger.debug(
            f"Creating access token for user ID: {str(user_id)[:10]}..."
        )
        self.logout_user(user_id)

        token = self.generate_token()
        current_time = datetime.now()
        expires_at = current_time + timedelta(hours=720)  # 30 days

        db_token = Tokens(token=token, expires_at=expires_at, user_id=user_id)
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

    def get_user_profile(self, user_id: UUID) -> Dict[str, Any]:
        """
        Get user profile information by user ID

        Args:
            user_id: The ID of the user

        Returns:
            Dictionary containing user profile information
        """
        stmt = select(Users).where(Users.id == user_id)
        result = self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        created_date = (
            user.created_at.strftime("%Y-%m-%d") if user.created_at else None
        )

        return {
            "email": user.email,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "registered_at": created_date,
        }

    def reset_password(self, token: str, password: str):
        """Changes a user's password"""
        user_data = self._validate_email_token(token)
        hashed_pw = self._hash_password(password)

        stmt = (
            update(Users)
            .where(Users.email == user_data.email)
            .values(password=hashed_pw)
        )
        self.db.execute(stmt)
        self.db.commit()

        # New secret token so that noone can reset the password during the 1hr window
        self.update_email_token(user_data.email)

        return user_data
