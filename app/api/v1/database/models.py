# External improts
from typing import List
from datetime import datetime
from uuid import UUID
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
    Numeric,
    CheckConstraint,
    event,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.dialects.postgresql import UUID as SQLUUID, JSONB

# Internal imports
from app.api.logger.logger import get_logger

logger = get_logger("app.database.models")


class Base(DeclarativeBase):
    pass


@event.listens_for(Base, "after_insert", propagate=True)
def log_insert(mapper, connection, target):
    model_name = target.__class__.__name__
    primary_key = get_primary_key_value(target)
    logger.info(f"Created {model_name} with id {str(primary_key)[:10]}...")


@event.listens_for(Base, "after_update", propagate=True)
def log_update(mapper, connection, target):
    model_name = target.__class__.__name__
    primary_key = get_primary_key_value(target)
    logger.info(f"Updated {model_name} with id {str(primary_key)[:10]}...")


@event.listens_for(Base, "after_delete", propagate=True)
def log_delete(mapper, connection, target):
    model_name = target.__class__.__name__
    primary_key = get_primary_key_value(target)
    logger.info(f"Deleted {model_name} with id {str(primary_key)[:10]}...")


def get_primary_key_value(target):
    """Extract the primary key value from a model instance."""
    try:
        if hasattr(target, "id"):
            return target.id
        for attr_name in dir(target):
            if "id" in attr_name.lower() and not attr_name.startswith("_"):
                return getattr(target, attr_name)
        return hex(id(target))
    except Exception as e:
        logger.warning(f"Error extracting primary key: {str(e)}")
        return hex(id(target))


class EmailTokens(Base):
    __tablename__ = "email_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    token: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )


class AdventureCategories(Base):
    __tablename__ = "adventure_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship
    starting_stories: Mapped[List["StartingStories"]] = relationship(
        "StartingStories",
        back_populates="category",
        cascade="all, delete-orphan",
    )


class StartingStories(Base):
    __tablename__ = "starting_stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("adventure_categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    story: Mapped[str] = mapped_column(String, nullable=False)
    image: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )

    # Relationship
    category: Mapped["AdventureCategories"] = relationship(
        "AdventureCategories",
        back_populates="starting_stories",
    )


class Users(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(SQLUUID, primary_key=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    all_actions: Mapped[List[str]] = mapped_column(JSONB, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relationships
    tokens: Mapped[List["Tokens"]] = relationship(
        "Tokens", back_populates="user", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["Reviews"]] = relationship(
        "Reviews", back_populates="user", cascade="all, delete-orphan"
    )
    payments: Mapped[List["Payments"]] = relationship(
        "Payments", back_populates="user", cascade="all, delete-orphan"
    )
    game_sessions: Mapped[List["GameSessions"]] = relationship(
        "GameSessions", back_populates="user", cascade="all, delete-orphan"
    )
    rate_limits: Mapped[List["RateLimit"]] = relationship(
        "RateLimit", back_populates="user", cascade="all, delete-orphan"
    )


class GameSessions(Base):
    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[UUID] = mapped_column(
        SQLUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    session_name: Mapped[str] = mapped_column(String, nullable=True)
    last_image: Mapped[str] = mapped_column(String, nullable=True)
    protagonist_name: Mapped[str] = mapped_column(String, nullable=False)
    inventory: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    stories: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relationship
    user: Mapped["Users"] = relationship(
        "Users", back_populates="game_sessions"
    )


class Reviews(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        SQLUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    rating: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("rating >= 1 AND rating <= 5"),
        nullable=False,
    )
    comment: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )

    # Relationship
    user: Mapped["Users"] = relationship("Users", back_populates="reviews")


class Tokens(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        SQLUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationship
    user: Mapped["Users"] = relationship("Users", back_populates="tokens")


class PaymentMethods(Base):
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship
    payments: Mapped[List["Payments"]] = relationship(
        "Payments",
        back_populates="payment_method",
        cascade="all, delete-orphan",
    )


class Payments(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        SQLUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    payment_method_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("payment_methods.id", ondelete="CASCADE"),
        nullable=False,
    )
    amount: Mapped[float] = mapped_column(Numeric, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )

    # Relationships
    user: Mapped["Users"] = relationship("Users", back_populates="payments")
    payment_method: Mapped["PaymentMethods"] = relationship(
        "PaymentMethods", back_populates="payments"
    )


class RateLimit(Base):
    __tablename__ = "rate_limits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        SQLUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    ip_address: Mapped[str] = mapped_column(String, nullable=True)
    endpoint_path: Mapped[str] = mapped_column(String, nullable=False)
    requests: Mapped[List[int]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relationship
    user: Mapped["Users"] = relationship(
        "Users", back_populates="rate_limits"
    )
