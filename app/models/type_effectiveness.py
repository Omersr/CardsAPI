
from sqlalchemy import Enum as PgEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .monster_card import CardType
from app.database import Base
from sqlalchemy import select
from deps import get_db
class TypeEffectiveness(Base):
    __tablename__ = "type_effectiveness"
    attacker_type: Mapped[CardType] = mapped_column(PgEnum(CardType, name="card_type_enum", native_enum=True),primary_key=True)
    defender_type: Mapped[CardType] = mapped_column(PgEnum(CardType, name="card_type_enum", native_enum=True),primary_key=True,)
    effective: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    @staticmethod
    def is_effective(attacker_type: CardType, defender_type: CardType) -> bool:
        db = get_db()
        with db as session:
            result = session.execute(
                select(TypeEffectiveness.effective).where(
                    TypeEffectiveness.attacker_type == attacker_type,
                    TypeEffectiveness.defender_type == defender_type
                )
            ).scalar_one_or_none()        
        return result if result is not None else False
