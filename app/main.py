from contextlib import asynccontextmanager
from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.routers import monster_cards
from app.routers import player
import app.models.type_effectiveness  # needed for table creation for now
from fastapi import FastAPI, Request
from app.database import SessionLocal
from app.database_context import _db_ctx
logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application...")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down...")



app = FastAPI(title="Cards App", lifespan=lifespan)

# This middleware is always called in http requests, it creates a new db session and sets it in the context variable 
# for the duration of the request, then closes it after the request is done. This allows us to use get_current_db() 
# to get the current db session in our models and services without having to pass it around explicitly.
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    db = SessionLocal()
    token = _db_ctx.set(db)
    try:
        response = await call_next(request)
        return response
    finally:
        _db_ctx.reset(token)
        db.close()

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"

app.mount(
    "/assets",
    StaticFiles(directory=str(ASSETS_DIR)),
    name="assets",
)

app.include_router(monster_cards.router)
app.include_router(player.router)