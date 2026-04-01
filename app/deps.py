from typing import Generator
from sqlalchemy.orm import Session

# Import your SessionLocal factory (usually defined in app/database.py)
from .database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()