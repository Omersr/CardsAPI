from contextvars import ContextVar
from sqlalchemy.orm import Session

# This acts as a global "storage slot" for the current session
_db_ctx: ContextVar[Session] = ContextVar("db_session")

def get_current_db() -> Session:
    session = _db_ctx.get(None)
    if session is None:
        raise RuntimeError("No database session found in current context")
    return session