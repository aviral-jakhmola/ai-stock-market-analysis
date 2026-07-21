import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes — provides a database session per request,
    and guarantees it's closed afterward even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Import models here so Base already exists
    from app.models.user import User
    from app.models.watchlist import Watchlist
    from app.models.search_history import SearchHistory

    Base.metadata.create_all(bind=engine)