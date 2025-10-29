import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine import make_url

# Helper function to ensure the database exists. Database creation logic is down below.
def ensure_database_exists(db_url: str):
    """
    Ensures the target Postgres database exists.
    If it doesn't, connect to 'postgres' and create it.
    """
    url = make_url(db_url)
    db_name = url.database
    admin_url = url.set(database="postgres")

    # 1) Try connecting to target DB
    try:
        tmp_engine = create_engine(db_url, future=True, pool_pre_ping=True)
        with tmp_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        tmp_engine.dispose()
        return
    except OperationalError:
        print(f"Database '{db_name}' not found, creating it...")

    # 2) Connect to default 'postgres' DB and create the target
    admin_engine = create_engine(admin_url, future=True, pool_pre_ping=True, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            print(f"Database '{db_name}' created 🎉")
        else:
            print(f"Database '{db_name}' already existed (race condition safe)")
    admin_engine.dispose()

load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # default fallback (useful for dev, prevents None)
    "postgresql+psycopg2://postgres:gunrtxh1@localhost:5432/cards"
)
ensure_database_exists(DATABASE_URL)
# Create the SQLAlchemy engine (sync)
engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,   # validates connections before using them
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Base for future models (even if we don’t have any yet), replaces the deprecated declarative_base
# Will be used for Base.metadata.create_all(engine)
class Base(DeclarativeBase):
    pass

# Simple helper to check DB connectivity
def db_ping() -> bool:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True





