
from sqlalchemy import Enum as PgEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .model_enums import CardType
from app.database import Base
from sqlalchemy import select
from app.database_context import get_current_db

class TypeEffectiveness(Base):
    __tablename__ = "type_effectiveness"
    attacker_type: Mapped[CardType] = mapped_column(PgEnum(CardType, name="card_type_enum", native_enum=True),primary_key=True)
    defender_type: Mapped[CardType] = mapped_column(PgEnum(CardType, name="card_type_enum", native_enum=True),primary_key=True,)
    effective: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    @staticmethod
    def effectiveness_value(attacker_type: CardType, defender_type: CardType) -> float:
        db = get_current_db()
        result = db.scalar(
        select(TypeEffectiveness.effective).where(
            TypeEffectiveness.attacker_type == attacker_type,
            TypeEffectiveness.defender_type == defender_type))
        if result is None:
            return 1.0
        return 2.0 if result else 0.5
