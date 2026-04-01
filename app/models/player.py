from __future__ import annotations

from typing import Optional, Any

from fastapi import HTTPException
from sqlalchemy import BigInteger, Enum as PgEnum, ForeignKey, String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column

from .model_enums import TeamType
from app.database import Base
from app.schemas.player import PlayerCreate
from app.models.monster_card import MonsterCard
from app.database_context import get_current_db


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    team: Mapped[Optional[TeamType]] = mapped_column(
        PgEnum(TeamType, name="team_type_enum", create_type=False, native_enum=True),
        nullable=True,
        default=TeamType.neutral,
        index=True,
    )
    monster_card_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("monster_cards.id"),
        nullable=True,
    )

    _UPDATABLE_FIELDS = {
        "name",
        "team",
        "monster_card_id",
    }

    @staticmethod
    def create_player(data: PlayerCreate) -> "Player":
        db = get_current_db()

        player = Player(
            name=data.name,
            team=data.team if hasattr(data, "team") else TeamType.neutral,
            monster_card_id=data.monster_card_id,
        )

        if player.monster_card_id is not None:
            card = MonsterCard.get_card(player.monster_card_id)
            if card is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"monster_card_id {player.monster_card_id} does not exist",
                )

        db.add(player)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to create player: {e.orig}") from e

        db.refresh(player)
        return player

    @staticmethod
    def get_player(player_id: int) -> Optional["Player"]:
        db = get_current_db()
        stmt = select(Player).where(Player.id == player_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_player_by_name(name: str) -> Optional["Player"]:
        db = get_current_db()
        stmt = select(Player).where(Player.name == name)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_players(
        *,
        limit: int = 20,
        offset: int = 0,
        team: Optional[TeamType] = None,
        name_search: Optional[str] = None,
    ) -> list["Player"]:
        db = get_current_db()
        stmt = select(Player).order_by(Player.id).limit(limit).offset(offset)

        if team is not None:
            stmt = stmt.where(Player.team == team)

        if name_search:
            stmt = stmt.where(Player.name.ilike(f"%{name_search}%"))

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def update_player(player_id: int, updates: dict[str, Any]) -> "Player":
        db = get_current_db()
        player = Player.get_player(player_id)
        if player is None:
            raise HTTPException(status_code=404, detail=f"player id {player_id} not found")

        clean = {k: v for k, v in updates.items() if k in Player._UPDATABLE_FIELDS}

        if "monster_card_id" in clean and clean["monster_card_id"] is not None:
            card = MonsterCard.get_card(clean["monster_card_id"])
            if card is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"monster_card_id {clean['monster_card_id']} does not exist",
                )

        for field, value in clean.items():
            setattr(player, field, value)

        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to update player: {e.orig}") from e

        db.refresh(player)
        return player

    @staticmethod
    def delete_player(player_id: int) -> None:
        db = get_current_db()
        player = Player.get_player(player_id)
        if player is None:
            raise HTTPException(status_code=404, detail=f"player id {player_id} not found")

        db.delete(player)
        db.commit()