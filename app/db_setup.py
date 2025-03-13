# External imports
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Internal imports
from app.api.v1.database.models import Base
from app.settings import settings

url = settings.DATABASE_URL

try:
    engine = create_engine(f"{url}", echo=True)
    print("Engine created successfully")
except Exception as e:
    print(f"Error creating engine: {str(e)}")


def init_db():
    """
    Called when main.py is run.
    Creates all tables in the database.
    """
    try:
        print("Attempting to create all tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {str(e)}")


def get_db():
    """
    Returns a session to the database.
    Used when changes are made to the db during runtime.
    """
    with Session(engine, expire_on_commit=False) as session:
        yield session
