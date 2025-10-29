from pydantic import BaseModel, Field
from typing import Optional
from app.models.monster_card import CardType
from app.schemas.base import ORMModel, InputModel


class MonsterCardBase(InputModel):
    #... means this field has no default value — it’s required
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    primary_type: CardType
    secondary_type: Optional[CardType] = None
    health: int = Field(..., ge=0) 
    attack: int = Field(..., ge=0)
    defense: int = Field(..., ge=0)
    speed: int = Field(..., ge=0)


class MonsterCardCreate(MonsterCardBase):
    """Schema for card creation requests."""
    pass

# Inherting from MonsterCardBase to avoid redundancy and ORMModel for ORM compatibility (json serialization)
class MonsterCardOut(ORMModel,MonsterCardBase):
    id: int # response model inherits ORMModel ⇒ from_attributes=True
