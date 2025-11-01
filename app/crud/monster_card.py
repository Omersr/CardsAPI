# app/crud/monster_card.py
from __future__ import annotations

from typing import Optional, Sequence, Any, Dict

from string import Template

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException


from app.models.monster_card import MonsterCard, CardType, DisplayType
from app.schemas.monster_card import MonsterCardCreate
from app.config import *



# --- Domain-level errors (so routers can translate to HTTP codes later) ---

class DuplicateNameError(Exception):
    """Raised when attempting to create/update a card with a duplicate name (unique violation)."""


class NotFoundError(Exception):
    """Raised when a card is not found for a given identifier."""


# --- CRUD helpers ---


from PIL import Image
from pathlib import Path

def _ensure_image_size(image_path: Path, target_size=(230, 150)) -> None:
    """
    Ensures an image has the correct size (230x150). 
    If not, resizes and overwrites the file in place.
    """
    if not image_path.exists():
        return
    try:
        with Image.open(image_path) as img:
            if img.size != target_size:
                resized = img.resize(target_size, Image.Resampling.LANCZOS)
                resized.save(image_path)
    except Exception as e:
        raise ValueError(f"[ERROR] Could not process image {image_path}: {e}")

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
    
    html_display_path =  HTML_FORMATS_DIR / display.value
    raw_html = html_display_path.read_text(encoding="utf-8")
    monster_filename = f"{card.name.capitalize().replace(' ', '_')}.png"
    _ensure_image_size(MONSTER_CARD_IMAGES_DIR / monster_filename)
    image_path = f"{PUBLIC_MONSTER_IMAGES_URL}/{monster_filename}"
    primary_type_image_path = f"{PUBLIC_TYPE_ICONS_URL}/{card.primary_type.value.lower()}_icon.png"
    secondary_type_image_path = f"{PUBLIC_TYPE_ICONS_URL}/{card.secondary_type.value.lower()}_icon.png"
    
    template = Template(raw_html)
    output_html = template.safe_substitute(
        name=card.name,
        description=card.description or "",
        primary_type_image_path = primary_type_image_path,
        secondary_type_image_path = secondary_type_image_path,
        health=card.health,
        attack=card.attack,
        defense=card.defense,
        speed=card.speed,
        image_path= image_path,  # optional if you have per-card images
    )
    return output_html  # Placeholder for actual HTML rendering logic

    