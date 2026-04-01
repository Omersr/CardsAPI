# app/models/item_card.py

from __future__ import annotations

from typing import List

from sqlalchemy import BigInteger, Boolean, String, ForeignKey, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column

from fastapi import HTTPException, status

from app.database import Base
from app.database_context import get_current_db


class ItemCard(Base):
    __tablename__ = "item_card"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    monster_card_id: Mapped[int] = mapped_column(ForeignKey("monster_cards.id"))
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    def create(**kwargs) -> "ItemCard":
        db = get_current_db()

        item = ItemCard(**kwargs)

        try:
            db.add(item)
            db.commit()
            db.refresh(item)
            return item
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ItemCard with this name already exists."
            )

    # -------------------------
    # READ - SINGLE
    # -------------------------
    @staticmethod
    def get_by_id(item_id: int) -> "ItemCard":
        db = get_current_db()

        stmt = select(ItemCard).where(ItemCard.id == item_id)
        item = db.execute(stmt).scalar_one_or_none()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ItemCard not found."
            )
        return item

    # -------------------------
    # READ - ALL
    # -------------------------
    @staticmethod
    def get_all() -> List["ItemCard"]:
        db = get_current_db()

        stmt = select(ItemCard)
        return list(db.execute(stmt).scalars().all())

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    def update(item_id: int, **kwargs) -> "ItemCard":
        db = get_current_db()

        item = ItemCard.get_by_id(item_id)

        for key, value in kwargs.items():
            if hasattr(item, key) and value is not None:
                setattr(item, key, value)

        try:
            db.commit()
            db.refresh(item)
            return item
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update failed (possibly duplicate name)."
            )

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    def delete(item_id: int) -> None:
        db = get_current_db()

        item = ItemCard.get_by_id(item_id)

        db.delete(item)
        db.commit()