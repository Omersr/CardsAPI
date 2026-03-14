# app/models/monster_card.py
from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base

class ItemCard(Base):
    __tablename__ = "item_card"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    monster_card_id: Mapped[int] = mapped_column(ForeignKey("monster_cards.id"))
    used = mapped_column(Boolean, nullable=False, default=False)

        
