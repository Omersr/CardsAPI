from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .deps import get_db
from .database import db_ping
from sqlalchemy import inspect
from app.database import engine, Base 
from app.models import monster_card  # ensure model is registered
from app.routers import monster_cards  # <-- import the router module


app = FastAPI(title="Cards App")

# We didn't do it for database because this executes when the app starts. We want to create database before that.
@app.on_event("startup")
def on_startup():
    # Create tables if they don’t exist (dev convenience; later we’ll switch to Alembic).
    inspector = inspect(engine)
    if "monster_cards" not in inspector.get_table_names():
        Base.metadata.create_all(bind=engine)


app.include_router(monster_cards.router)

