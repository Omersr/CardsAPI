from __future__ import annotations

import logging
from typing import List, Optional, Annotated, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.player import *
from app.schemas.player import *

router = APIRouter(prefix="/player", tags=["player"])
logger = logging.getLogger("uvicorn.error")
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=PlayerOut, status_code=status.HTTP_201_CREATED)
def create_player_route(payload: PlayerCreate, db: DbSession):
    try:
        return Player.create_player(payload)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Player: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/", response_model=List[PlayerOut])
def list_players_route(
    db: DbSession,
    limit: int = 20,
    offset: int = 0,
    team: Optional[TeamType] = None,
    name_search: Optional[str] = None,
):
    try:
        return Player.list_players(
            limit=limit,
            offset=offset,
            team=team,
            name_search=name_search,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing Players: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/{player_id:int}", response_model=PlayerOut)
def get_player_route(player_id: int, db: DbSession):
    try:
        player = Player.get_player(player_id)
        if not player:
            logger.error(f"Player with id {player_id} not found.")
            return Response(status_code=404, content=f"Player with id {player_id} not found.")
        return player
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Player with id {player_id}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/by-name/{name}", response_model=PlayerOut)
def get_player_by_name_route(name: str, db: DbSession):
    try:
        player = Player.get_player_by_name(name)
        if not player:
            logger.error(f"Player with name {name} not found.")
            return Response(status_code=404, content=f"Player with name {name} not found.")
        return player
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Player with name {name}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.patch("/{player_id:int}", response_model=PlayerOut)
def patch_player_route(player_id: int, payload: PlayerUpdate, db: DbSession):
    try:
        updates: Dict[str, Any] = payload.model_dump(exclude_unset=True)
        return Player.update_player(player_id, updates)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Player with id {player_id}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.delete("/{player_id:int}", status_code=status.HTTP_204_NO_CONTENT)
def remove_player_route(player_id: int, db: DbSession):
    try:
        Player.delete_player(player_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Player with id {player_id}: {str(e)}")
        return Response(status_code=500, content=str(e))
