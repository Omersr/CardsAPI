# app/crud/monster_card.py
from __future__ import annotations

from typing import Optional, Sequence, Any, Dict

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.monster_card import MonsterCard, CardType, DisplayType
from app.schemas.monster_card import MonsterCardCreate
import os
from pathlib import Path


# --- Domain-level errors (so routers can translate to HTTP codes later) ---

class DuplicateNameError(Exception):
    """Raised when attempting to create/update a card with a duplicate name (unique violation)."""


class NotFoundError(Exception):
    """Raised when a card is not found for a given identifier."""


# --- CRUD helpers ---

def create_card(db: Session, data: MonsterCardCreate) -> MonsterCard:
    """
    Insert a new MonsterCard.
    Business rule: if secondary_type is None -> set to primary_type.
    Raises DuplicateNameError on unique-name conflict.
    """
    secondary = data.secondary_type or data.primary_type

    card = MonsterCard(
        name=data.name,
        description=data.description,
        primary_type=data.primary_type,
        secondary_type=secondary,
        health=data.health,
        attack=data.attack,
        defense=data.defense,
        speed=data.speed,
    )

    db.add(card)
    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    db.refresh(card)
    return card


def get_card(db: Session, card_id: int) -> Optional[MonsterCard]:
    """Fetch a card by its primary key."""
    stmt = select(MonsterCard).where(MonsterCard.id == card_id)
    return db.execute(stmt).scalar_one_or_none()


def get_card_by_name(db: Session, name: str) -> Optional[MonsterCard]:
    """Fetch a card by unique name."""
    stmt = select(MonsterCard).where(MonsterCard.name == name)
    return db.execute(stmt).scalar_one_or_none()


def list_cards(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    primary_type: Optional[CardType] = None,
    secondary_type: Optional[CardType] = None,
    name_search: Optional[str] = None,
) -> Sequence[MonsterCard]:
    """
    List cards with simple filtering and pagination.
    - Filter by primary/secondary type (exact match)
    - name_search does ILIKE '%term%' on name
    """
    stmt = select(MonsterCard).order_by(MonsterCard.id).limit(limit).offset(offset)

    if primary_type is not None:
        stmt = stmt.where(MonsterCard.primary_type == primary_type)
    if secondary_type is not None:
        stmt = stmt.where(MonsterCard.secondary_type == secondary_type)
    if name_search:
        # Postgres ILIKE (case-insensitive)
        stmt = stmt.where(MonsterCard.name.ilike(f"%{name_search}%"))

    return db.execute(stmt).scalars().all()


# Allowed fields for partial updates
_UPDATABLE_FIELDS = {
    "name",
    "description",
    "primary_type",
    "secondary_type",
    "health",
    "attack",
    "defense",
    "speed",
}

def update_card(db: Session, card_id: int, updates: Dict[str, Any]) -> MonsterCard:
    """
    Partially update a card.
    - Only fields in _UPDATABLE_FIELDS are applied.
    - If secondary_type is None (or omitted) but primary_type provided, secondary_type auto-fills to primary_type.
    Raises NotFoundError if card doesn't exist.
    Raises DuplicateNameError on unique-name conflict.
    """
    card = get_card(db, card_id)
    if card is None:
        raise NotFoundError(f"Card id {card_id} not found.")

    # Sanitize allowed fields only
    clean: Dict[str, Any] = {k: v for k, v in updates.items() if k in _UPDATABLE_FIELDS}

    # Apply incoming changes
    for field, value in clean.items():
        setattr(card, field, value)

    # Auto-fill secondary_type when appropriate
    if "primary_type" in clean and ("secondary_type" not in clean or clean.get("secondary_type") is None):
        card.secondary_type = card.primary_type

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if "name" in clean:
            raise DuplicateNameError(f"A card named '{clean['name']}' already exists.") from e
        raise

    db.refresh(card)
    return card


def delete_card(db: Session, card_id: int) -> None:
    """
    Hard delete a card by id.
    Raises NotFoundError if it doesn't exist.
    """
    card = get_card(db, card_id)
    if card is None:
        raise NotFoundError(f"Card id {card_id} not found.")

    db.delete(card)
    db.commit()


def display_monster_card(db: Session, card_id: int, display: DisplayType) -> str:
    """
    Displays a card in an html format, must be one of the predefined formats.
    """
    card = get_card(db, card_id)
    if card is None:
        raise NotFoundError(f"Card id {card_id} not found.")
    HTML_FORMATS = Path(os.getenv("HTML_FORMATS"))
    file_path =  HTML_FORMATS / display.value
    return file_path.read_text(encoding="utf-8")  # Placeholder for actual HTML rendering logic

    