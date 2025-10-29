# app/models/monster_card.py
from enum import Enum
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, Enum as PgEnum, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class CardType(str, Enum):
    arms = "arms"
    dark = "dark"
    earth = "earth"
    fire = "fire"
    frost = "frost"
    light = "light"
    lightning = "lightning"
    magic = "magic"
    ore = "ore"
    poison = "poison"
    water = "water"
    wind = "wind"
    plant = "plant"

class MonsterCard(Base):
    __tablename__ = "monster_cards"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # name must be unique (interpreting your “string identity” as unique)
    # Also adding an index for faster lookups in index = true
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    primary_type: Mapped[CardType] = mapped_column(
        PgEnum(CardType, name="card_type_enum", create_type=True, native_enum=True),
        nullable=False,
        index=True,
    )
    secondary_type: Mapped[Optional[CardType]] = mapped_column(
        PgEnum(CardType, name="card_type_enum", create_type=False, native_enum=True),
        nullable=True,
        index=True,
    )

    health: Mapped[int] = mapped_column(Integer, nullable=False)
    attack: Mapped[int] = mapped_column(Integer, nullable=False)
    defense: Mapped[int] = mapped_column(Integer, nullable=False)
    speed: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("name", name="uq_monster_cards_name"),
        # Basic non-negative sanity checks (we’ll add richer validation in API later if you want)
        CheckConstraint("health >= 0", name="ck_monster_cards_health_nonneg"),
        CheckConstraint("attack >= 0", name="ck_monster_cards_attack_nonneg"),
        CheckConstraint("defense >= 0", name="ck_monster_cards_defense_nonneg"),
        CheckConstraint("speed >= 0", name="ck_monster_cards_speed_nonneg"),
        # We didn't create index on name because of the unique constraint, but we can create a composite index on types
        Index("ix_monster_cards_types", "primary_type", "secondary_type"),
    )
