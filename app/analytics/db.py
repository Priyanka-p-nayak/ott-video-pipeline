"""Database engine and session setup for SQLAlchemy."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

# The engine represents the connection configuration to the database
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory for creating new database sessions (transactions)
SessionLocal = sessionmaker(bind=engine)

# Base is the foundation for all our SQLAlchemy models (tables)
Base = declarative_base()


def get_session():
    """Create and return a new database session."""
    return SessionLocal()


def init_db():
    """Create all tables defined by models that inherit from Base."""
    Base.metadata.create_all(bind=engine)