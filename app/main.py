from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from app.database import engine, Base 
from app.routers import monster_cards  # <-- import the router module
from app.routers import player
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

# Mounting assets directory to serve static files
app = FastAPI(title="Cards App")
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
app.mount(
    "/assets",
    StaticFiles(directory=str(ASSETS_DIR)),
    name="assets"
)

# We didn't do it for database because this executes when the app starts. We want to create database before that.
@app.on_event("startup")
def on_startup():
    # Create tables if they don’t exist (dev convenience; later we’ll switch to Alembic).
    inspector = inspect(engine)
    if "monster_cards" not in inspector.get_table_names() or "players" not in inspector.get_table_names():
        Base.metadata.create_all(bind=engine)



app.include_router(monster_cards.router)
app.include_router(player.router)


