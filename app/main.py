from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .deps import get_db
from .database import db_ping

app = FastAPI(title="Card App (Step 1)")

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)) -> dict:
    """
    Not CRUD—just demonstrates that FastAPI can open a DB session.
    If the connection string is wrong or DB is down, this will error.
    """
    db_ping()  # runs SELECT 1
    return {"db": "connected"}
