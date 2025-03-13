from typing import Optional, List
from datetime import datetime
from uuid import UUID
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
    Numeric,
    SmallInteger,
    Date,
    CheckConstraint,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.dialects.postgresql import UUID as SQLUUID, JSONB


class Base(DeclarativeBase):
    pass


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
    action: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )

    # Relationship
    category: Mapped["AdventureCategories"] = relationship(
        "AdventureCategories",
        back_populates="starting_stories",
        cascade="all, delete-orphan",
    )


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
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


class GameSessions(Base):
    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    session_name: Mapped[str] = mapped_column(String, nullable=False)
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
        "Users", back_populates="game_sessions", cascade="all, delete-orphan"
    )


class Reviews(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
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
    user: Mapped["Users"] = relationship(
        "Users", back_populates="reviews", cascade="all, delete-orphan"
    )


class Tokens(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationship
    user: Mapped["Users"] = relationship(
        "Users", back_populates="tokens", cascade="all, delete-orphan"
    )


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
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
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
    user: Mapped["Users"] = relationship(
        "Users", back_populates="payments", cascade="all, delete-orphan"
    )
    payment_method: Mapped["PaymentMethods"] = relationship(
        "PaymentMethods",
        back_populates="payments",
        cascade="all, delete-orphan",
    )
