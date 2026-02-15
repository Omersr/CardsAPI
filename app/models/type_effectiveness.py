
from sqlalchemy import Enum as PgEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .monster_card import CardType
from app.database import Base

class TypeEffectiveness(Base):
    __tablename__ = "type_effectiveness"

    attacker_type: Mapped[CardType] = mapped_column(
        PgEnum(CardType, name="card_type_enum", native_enum=True),
        primary_key=True,
    )

    defender_type: Mapped[CardType] = mapped_column(
        PgEnum(CardType, name="card_type_enum", native_enum=True),
        primary_key=True,
    )

    effective: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
