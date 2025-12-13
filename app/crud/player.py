# app/crud/monster_player.py
from __future__ import annotations

from typing import Optional, Sequence, Any, Dict

from string import Template

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud.monster_card import get_card
from app.models.player import Player, TeamType
from app.schemas.player import *
from app.config import *


class DuplicateNameError(Exception):
    """Raised when attempting to create/update a card with a duplicate name (unique violation)."""

class NotFoundError(Exception):
    """Raised when a player is not found for a given identifier."""


# --- CRUD helpers ---


def create_player(db: Session, data: PlayerCreate) -> Player:
    """
    Insert a new Player.
    Business rule: if secondary_type is None -> set to primary_type.
    Raises DuplicateNameError on unique-name conflict.
    """

    player = Player(
        name=data.name,
        monster_card_id = data.monster_card_id,
    )
    if get_card(db, player.monster_card_id) is None:
        raise HTTPException(status_code=400, detail=f"monster_card_id {player.monster_card_id} does not exist.")
    db.add(player)
    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    db.refresh(player)
    return player


def get_player(db: Session, player_id: int) -> Optional[Player]:
    """Fetch a player by its primary key."""
    stmt = select(Player).where(Player.id == player_id)
    return db.execute(stmt).scalar_one_or_none()


def get_player_by_name(db: Session, name: str) -> Optional[Player]:
    """Fetch a player by unique name."""
    stmt = select(Player).where(Player.name == name)
    return db.execute(stmt).scalar_one_or_none()


def list_players(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    team: Optional[TeamType] = None,
    name_search: Optional[str] = None,
) -> Sequence[Player]:
    """
    List players with simple filtering and pagination.
    - Filter by primary/secondary type (exact match)
    - name_search does ILIKE '%term%' on name
    """
    stmt = select(Player).order_by(Player.id).limit(limit).offset(offset)
    if team is not None:
        stmt = stmt.where(Player.team == team)
    if name_search:
        # Postgres ILIKE (case-insensitive)
        stmt = stmt.where(Player.name.ilike(f"%{name_search}%"))

    return db.execute(stmt).scalars().all()


# Allowed fields for partial updates
_UPDATABLE_FIELDS = {
    "name",
    "team",
    "monster_card_id"
}

def update_player(db: Session, player_id: int, updates: Dict[str, Any]) -> Player:
    """
    Partially update a player.
    - Only fields in _UPDATABLE_FIELDS are applied.
    - If secondary_type is None (or omitted) but primary_type provided, secondary_type auto-fills to primary_type.
    Raises NotFoundError if player doesn't exist.
    Raises DuplicateNameError on unique-name conflict.
    """
    player = get_player(db, player_id)
    if player is None:
        raise NotFoundError(f"player id {player_id} not found.")

    # Sanitize allowed fields only
    clean: Dict[str, Any] = {k: v for k, v in updates.items() if k in _UPDATABLE_FIELDS}

    # Apply incoming changes
    for field, value in clean.items():
        setattr(player, field, value)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise
    if "name" in clean:
        raise DuplicateNameError(f"A player named '{clean['name']}' already exists.") from e
    db.refresh(player)
    return player


def delete_player(db: Session, player_id: int) -> None:
    """
    Hard delete a player by id.
    Raises NotFoundError if it doesn't exist.
    """
    player = get_player(db, player_id)
    if player is None:
        raise NotFoundError(f"player id {player_id} not found.")
    db.delete(player)
    db.commit()

