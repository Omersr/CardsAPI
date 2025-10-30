from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from app.database import engine, Base 
from app.routers import monster_cards  # <-- import the router module
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os


app = FastAPI(title="Cards App")
MONSTER_CARD_IMAGES = Path(os.getenv("MONSTER_CARD_IMAGES"))
TYPES_ICONS = Path(os.getenv("TYPES_ICONS"))

# We didn't do it for database because this executes when the app starts. We want to create database before that.
@app.on_event("startup")
def on_startup():
    # Create tables if they don’t exist (dev convenience; later we’ll switch to Alembic).
    inspector = inspect(engine)
    if "monster_cards" not in inspector.get_table_names():
        Base.metadata.create_all(bind=engine)

app.mount(
    "/monster-images",
    StaticFiles(directory=str(MONSTER_CARD_IMAGES)),
    name="monster-images"
)

# Serve type icons at /type-icons
app.mount(
    "/type-icons",
    StaticFiles(directory=str(TYPES_ICONS)),
    name="type-icons"
)


app.include_router(monster_cards.router)


