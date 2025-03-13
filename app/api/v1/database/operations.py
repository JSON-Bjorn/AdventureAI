# External imports
from typing import Dict
from sqlalchemy.orm import Session
import bcrypt
import secrets
import base64
from datetime import datetime, timedelta
import re

# Internal imports
from app.api.v1.database.models import Users, Tokens
from app.api.v1.validation.schemas import UserCreate


class DatabaseOperations:
    def __init__(self, db: Session):
        self.db = db

    def get_story(self, story_id: str):
        # Placeholder method
        return {"story": "You are a cat, chasing a mouse around the house."}

    def save_game(self, context: Dict):
        # Post game save to db
        pass

    def load_game(self, game_id: str):
        # Get the game sve from db
        pass

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        is_valid = re.match(email_pattern, email)
        return bool(is_valid)

    def _check_existing_user(self, email: str) -> bool:
        """Check if a user with the given email already exists"""
        existing_user = (
            self.db.query(Users).filter(Users.email == email).first()
        )

        return bool(existing_user)

    def validate_token(self, token: str) -> Dict:
        """Validate a token and return user info if valid"""
        db_token = self.db.query(Tokens).filter(Tokens.token == token).first()

        if not db_token:
            return {"valid": False, "error": "Token not found"}

        current_time = datetime.now()

        if db_token.expires_at < current_time:
            return {"valid": False, "error": "Token expired"}

        return {"valid": True, "user_id": db_token.user_id}

    def create_user(self, user_data: UserCreate) -> Dict:
        """Create a new user in the database"""
        # Validate email format
        if not self._validate_email(user_data.email):
            raise ValueError("Invalid email format")

        # Check if user already exists
        if self._check_existing_user(user_data.email):
            raise ValueError("User with this email already exists")

        # Hash the password
        password_bytes = user_data.password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        hashed_password_str = hashed_password.decode("utf-8")

        # Create the user
        db_user = Users(
            email=user_data.email,
            password=hashed_password_str,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )

        # Add the user to the database
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        # Get access token
        access_token = self._create_access_token(db_user.id)

        return {"access_token": access_token}

    def _create_access_token(self, user_id: int) -> str:
        """Create an access token for the user"""
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
