from __future__ import annotations

from typing import List, Optional, Any

from fastapi import HTTPException, status
from sqlalchemy import BigInteger, Boolean, ForeignKey, String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database_context import get_current_db


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
    def delete(action_card_id: int) -> None:
        db = get_current_db()
        action_card = ActionCard.get_by_id(action_card_id)

        db.delete(action_card)
        db.commit()