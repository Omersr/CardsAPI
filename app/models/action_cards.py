from __future__ import annotations

from string import Template
from typing import List, Optional, Any

from fastapi import HTTPException, status
from sqlalchemy import BigInteger, Boolean, ForeignKey, String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column

from string import Template

from app.config import ACTION_CARD_IMAGES_DIR, HTML_ACTION_CARD_TEMPLATE, PUBLIC_ACTION_CARD_IMAGES_URL
from app.database import Base
from app.database_context import get_current_db
from app.services.cards_service import ensure_image_size


class ActionCard(Base):
    __tablename__ = "action_card"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    monster_card_id: Mapped[int] = mapped_column(ForeignKey("monster_cards.id"), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    @staticmethod
    def create(**kwargs) -> "ActionCard":
        db = get_current_db()
        action_card = ActionCard(**kwargs)

        try:
            db.add(action_card)
            db.commit()
            db.refresh(action_card)
            return action_card
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="ActionCard with this name already exists."
            )

    @staticmethod
    def get_by_id(action_card_id: int) -> "ActionCard":
        db = get_current_db()

        stmt = select(ActionCard).where(ActionCard.id == action_card_id)
        action_card = db.execute(stmt).scalar_one_or_none()

        if not action_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ActionCard not found."
            )
        return action_card

    @staticmethod
    def get_all(
        limit: int = 20,
        offset: int = 0,
        used: Optional[bool] = None,
        monster_card_id: Optional[int] = None,
        name_search: Optional[str] = None,
    ) -> List["ActionCard"]:
        db = get_current_db()

        stmt = select(ActionCard)

        if used is not None:
            stmt = stmt.where(ActionCard.used == used)

        if monster_card_id is not None:
            stmt = stmt.where(ActionCard.monster_card_id == monster_card_id)

        if name_search:
            stmt = stmt.where(ActionCard.name.ilike(f"%{name_search}%"))

        stmt = stmt.offset(offset).limit(limit)

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def update(action_card_id: int, **kwargs: Any) -> "ActionCard":
        db = get_current_db()
        action_card = ActionCard.get_by_id(action_card_id)

        allowed_fields = {"name", "description", "monster_card_id", "used"}

        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(action_card, key, value)

        try:
            db.commit()
            db.refresh(action_card)
            return action_card
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Update failed. ActionCard name may already exist."
            )

    @staticmethod
    def display_action_card(card_id: int) -> str:
        card = ActionCard.get_by_id(card_id)
        if card is None:
            raise HTTPException(status_code=404, detail=f"Card id {card_id} not found")

        raw_html = HTML_ACTION_CARD_TEMPLATE.read_text(encoding="utf-8")

        # same filename logic (no spaces)
        action_filename = f"{card.name.title()}.png"

        # filesystem path (for Python / PIL)
        full_image_path = ACTION_CARD_IMAGES_DIR / action_filename
        ensure_image_size(full_image_path)

        # public URL (for browser)
        image_path = f"{PUBLIC_ACTION_CARD_IMAGES_URL}/{action_filename}"

        template = Template(raw_html)
        output_html = template.safe_substitute(
            name=card.name,
            description=card.description or "",
            image_path=image_path,
        )

        return output_html
    
    @staticmethod
    def delete(item_id: int) -> None:
        db = get_current_db()
        action = ActionCard.get_by_id(item_id)
        db.delete(action)
        db.commit()