from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base 
from app.routers import monster_cards  # <-- import the router module
from app.routers import player
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import app.models.type_effectiveness # <- need this for now to create the table, when we will create the routes this can go
import logging
logger = logging.getLogger("uvicorn.error")



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
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application...")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down...")

app = FastAPI(title="Cards App", lifespan=lifespan)
app.include_router(monster_cards.router)
app.include_router(player.router)


