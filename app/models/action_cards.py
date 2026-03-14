# app/models/monster_card.py
from typing import Optional

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.database import Base

class ActionCard(Base):
    __tablename__ = "action_cards"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # name must be unique (interpreting your “string identity” as unique)
    # Also adding an index for faster lookups in index = true
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    player_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"), nullable=True)
    used = mapped_column(Boolean, nullable=False, default=False)

        
