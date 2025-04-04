from fastapi import Depends
from app.db_setup import get_db
from sqlalchemy.orm import Session
from sqlalchemy import insert, text
from app.api.v1.database.models import (
    AdventureCategories,
    StartingStories,
    Users,
    GameSessions,
    Reviews,
    Tokens,
    PaymentMethods,
    Payments,
)
from datetime import datetime, timedelta
import uuid
import bcrypt
from app.api.v1.database.setup.base64converter import img1, img2, img3


def fill_db(session: Session = Depends(get_db)):
    # Execute each function in sequence and commit after each step
    # to ensure foreign keys are available for dependent tables
    categories(session)
    session.commit()

    starting_stories(session)
    session.commit()

    game_sessions(session)
    session.commit()

    reviews(session)
    session.commit()

    tokens(session)
    session.commit()

    payment_methods(session)
    session.commit()

    payments(session)
    session.commit()

    print("All data has been successfully inserted!")


def categories(session: Session):
    print("Inserting categories...")
    # First clear existing data if any
    session.execute(
        text("TRUNCATE adventure_categories RESTART IDENTITY CASCADE")
    )

    categories = [
        {"name": "Fantasy"},
        {"name": "Horror"},
        {"name": "Science Fiction"},
    ]
    for category in categories:
        session.execute(insert(AdventureCategories).values(**category))
    session.flush()
    print("Categories inserted successfully")


def starting_stories(session: Session):
    print("Inserting starting stories...")
    # Make sure StartingStories has the correct structure (no action field)
    stories = [
        {
            "category_id": 1,  # Fantasy
            "image": img1,
            "story": """
You paused to catch your breath as you reached the top of the old tower. Sunlight filtered through cracked windows, illuminating the object you had been searching for—a crown, split in two, resting on a stone pedestal.
For years, unusual cold seasons had troubled the kingdom since the crown's separation. Village elders spoke of balance that could be restored, while others whispered that its power should be relinquished entirely.
You studied the artifact with curiosity.
""",
        },
        {
            "category_id": 2,  # Horror
            "image": img2,
            "story": """
Your fingers clawed at the wet earth as the sinkhole widened beneath the basement floor.
"Help!" your scream echoed, but the realtor had left hours ago.
As you slipped further down, your flashlight beam caught glimpses of impossible architecture below—stone corridors older than human civilization, walls inscribed with symbols that hurt your eyes, and something massive shifting in the darkness.
The fall lasted seconds but felt eternal. Now, bleeding and disoriented in a chamber that shouldn't exist, you heard scraping sounds approaching from multiple tunnels.
""",
        },
        {
            "category_id": 3,  # Science Fiction
            "image": img3,
            "story": """
You crashed to the deck as the transport's rear section tore away, venting atmosphere and three screaming soldiers into the void. Emergency lights bathed the corridor in crimson.
"Hostiles on the hull!" the Lieutenant shouted, his voice distorted through the comm as your helmet sealed automatically. "Defense turrets were deactivated!"
Your first mission, and the Ascendant station had already killed half the squad. Something had hacked their approach codes.
A section of wall buckled inward with a tortured screech of metal. Behind it, you glimpsed movement—neither human nor mechanical—slithering through the breach.
""",
        },
    ]
    for story in stories:
        session.execute(insert(StartingStories).values(**story))
    session.flush()
    print("Starting stories inserted successfully")


def game_sessions(session: Session):
    print("Inserting game sessions...")
    # Get user IDs from database
    user_result = session.execute(text("SELECT id FROM users")).fetchall()
    user_ids = [row[0] for row in user_result]

    if not user_ids:
        print("No users found, skipping game sessions")
        return

    if len(user_ids) < 2:
        print("Not enough users found, adding only available game sessions")

    games = []

    if len(user_ids) > 0:
        games.append(
            {
                "user_id": user_ids[0],
                "session_name": "Björn's Quest",
                "protagonist_name": "Sir Pryse; bat. 6th",
                "inventory": ["backdoor", "spit", "will-power"],
                "stories": [
                    {
                        "story": "You enter the dark cave, sword drawn.",
                        "action": "enter cave",
                        "dice_success": True,
                    },
                    {
                        "story": "Dark grumbling is heard from the depths; 'OUCH WRONG CAVE!'",
                        "action": "go even deeper",
                        "dice_success": False,
                    },
                    {
                        "story": "You turn around and leave the cave. Defeated, you fall asleep on the couch.",
                        "action": "file for divorce",
                        "dice_success": False,
                    },
                ],
            }
        )

    if len(user_ids) > 1:
        games.append(
            {
                "user_id": user_ids[1],
                "session_name": "Felix's Quest",
                "protagonist_name": "Captain Cuck, sitter of the chair",
                "inventory": ["lube", "camera", "penis pump"],
                "stories": [
                    {
                        "story": "You observe your wife and the stranger from the nearby closet.",
                        "action": "Touch myself",
                        "dice_success": True,
                    },
                    {
                        "story": "You are about to cum when the girl turns to you and says 'I'm sorry, I'm not into that'.",
                        "action": "i do a sick one-liner and join the fun",
                        "dice_success": False,
                    },
                    {
                        "story": "You leave the room in shame and confusion.",
                        "action": "I peep through the keyhole",
                        "dice_success": True,
                    },
                ],
            }
        )

    for game in games:
        session.execute(insert(GameSessions).values(**game))

    session.flush()
    print("Game sessions inserted successfully")


def reviews(session: Session):
    print("Inserting reviews...")
    # Get user IDs from database - using proper SQLAlchemy 2.0 syntax with text()
    user_result = session.execute(text("SELECT id FROM users")).fetchall()
    user_ids = [row[0] for row in user_result]

    if not user_ids:
        print("No users found, skipping reviews")
        return

    reviews = []

    if len(user_ids) > 0:
        reviews.append(
            {
                "user_id": user_ids[0],
                "rating": 5,
                "comment": "Amazing game, I love it!",
            }
        )

    if len(user_ids) > 1:
        reviews.append(
            {
                "user_id": user_ids[1],
                "rating": 5,
                "comment": "Saved my marriage!",
            }
        )

    for review in reviews:
        session.execute(insert(Reviews).values(**review))

    session.flush()
    print("Reviews inserted successfully")


def tokens(session: Session):
    print("Inserting tokens...")
    # Get user IDs from database
    user_result = session.execute(text("SELECT id FROM users")).fetchall()
    user_ids = [row[0] for row in user_result]

    if not user_ids:
        print("No users found, skipping tokens")
        return

    now = datetime.now()
    tokens = []

    # Create tokens only for users that exist
    for i, user_id in enumerate(user_ids):
        tokens.append(
            {
                "user_id": user_id,
                "token": str(uuid.uuid4()),
                "expires_at": now
                + timedelta(
                    days=(i + 1) * 7
                ),  # Different expiration for each token
            }
        )

    for token in tokens:
        session.execute(insert(Tokens).values(**token))

    session.flush()
    print("Tokens inserted successfully")


def payment_methods(session: Session):
    print("Inserting payment methods...")
    # First clear existing data if any
    session.execute(text("TRUNCATE payment_methods RESTART IDENTITY CASCADE"))

    methods = [
        {"name": "Credit Card"},
        {"name": "PayPal"},
        {"name": "Stripe"},
        {"name": "Bank Transfer"},
    ]
    for method in methods:
        session.execute(insert(PaymentMethods).values(**method))

    session.flush()
    print("Payment methods inserted successfully")


def payments(session: Session):
    print("Inserting payments...")
    # Get user IDs from database
    user_result = session.execute(text("SELECT id FROM users")).fetchall()
    user_ids = [row[0] for row in user_result]

    if not user_ids:
        print("No users found, skipping payments")
        return

    payments = []

    # Add payments only for users that exist
    payment_amounts = [19.99, 9.99]

    for i, user_id in enumerate(user_ids):
        if i < len(payment_amounts):
            payments.append(
                {
                    "user_id": user_id,
                    "payment_method_id": (i % 4)
                    + 1,  # Cycle through payment methods 1-4
                    "amount": payment_amounts[i],
                }
            )

    for payment in payments:
        session.execute(insert(Payments).values(**payment))

    session.flush()
    print("Payments inserted successfully")


if __name__ == "__main__":
    from app.db_setup import get_db

    session = next(get_db())
    try:
        fill_db(session=session)
        print("Database filled with dummy data successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error filling database: {str(e)}")
    finally:
        session.close()
