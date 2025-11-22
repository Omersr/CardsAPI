from __future__ import annotations

from typing import List, Optional, Annotated, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.deps import get_db
from app.database import SessionLocal
from app.models.player import *
from app.schemas.player import *
from app.crud.player import *
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/player", tags=["player"])



DbSession = Annotated[Session, Depends(get_db)]


# --- Update schema (all fields optional for PATCH) ---



# --- Endpoints ---

@router.post("/", response_model=PlayerOut, status_code=status.HTTP_201_CREATED)
def create_player_route(payload: PlayerCreate, db: DbSession):
    try:
        return create_player(db, payload)
    except Exception as e:
        # 409 Conflict for unique violation
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/", response_model=List[PlayerOut])
def list_players_route(
    db: DbSession,
    limit: int = 20,
    offset: int = 0,
    team: Optional[TeamType] = None,
    name_search: Optional[str] = None,
):
    return list_players(
        db,
        limit=limit,
        offset=offset,
        team=team,
        name_search=name_search,
    )


@router.get("/{player_id:int}", response_model=PlayerOut)
def get_player_route(player_id: int, db: DbSession):
    player = get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="player not found.")
    return player


    

@router.get("/by-name/{name}", response_model=PlayerOut)
def get_player_by_name_route(name: str, db: DbSession):
    player = get_player_by_name(db, name)
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="player not found.")
    return player




@router.patch("/{player_id:int}", response_model=PlayerOut)
def patch_player_route(player_id: int, payload: PlayerUpdate, db: DbSession):
    updates: Dict[str, Any] = payload.model_dump(exclude_unset=True)
    try:
        return update_player(db, player_id, updates)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{player_id:int}", status_code=status.HTTP_204_NO_CONTENT)
def remove_player_route(player_id: int, db: DbSession):
    try:
        delete_player(db, player_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

