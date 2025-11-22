# app/models/monster_card.py
from enum import Enum
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, Enum as PgEnum, Integer, String, Text, UniqueConstraint, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


from app.database import Base



class TeamType(str, Enum):
    bull = "bull"
    owl = "owl"
    swordfish = "swordfish"
    neutral = "neutral"
    @classmethod
    def _missing_(cls, value):
        # Whenever an invalid value is passed, return neutral
        return cls.neutral

class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # name must be unique (interpreting your “string identity” as unique)
    # Also adding an index for faster lookups in index = true
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)

    team: Mapped[Optional[TeamType]] = mapped_column(
        PgEnum(TeamType, name="team_type_enum", create_type=False, native_enum=True),
        nullable=True,
        default=TeamType.neutral,
        index=True,
    )
    monster_card_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("monster_cards.id"), nullable=True
    )
        
