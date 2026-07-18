import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from app.config import DATABASE_URL
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_session():
    return SessionLocal()

def init_db(max_retries: int = 10, retry_delay_seconds: int = 3) -> None:
    # Local import prevents circular dependency with app.models.event
    from app.models.event import ViewerEvent
    
    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables ready")
            return
        except OperationalError as e:
            logger.warning(f"Database not ready yet (attempt {attempt}/{max_retries}): {str(e)}")
            time.sleep(retry_delay_seconds)
    raise RuntimeError("Could not connect to the database after multiple retries")
