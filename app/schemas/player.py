from pydantic import BaseModel, Field
from typing import Optional
from app.models.player import TeamType
from app.schemas.base import ORMModel, InputModel


class PlayerBase(InputModel):
    #... means this field has no default value — it’s required
    name: str = Field(..., min_length=1, max_length=255)
    team: TeamType
    monster_card_id: Optional[int] = None


class PlayerCreate(PlayerBase):
    """Schema for card creation requests."""
    pass

# Inherting from MonsterCardBase to avoid redundancy and ORMModel for ORM compatibility (json serialization)
class PlayerOut(ORMModel,PlayerBase):
    id: int # response model inherits ORMModel ⇒ from_attributes=True
    
class PlayerUpdate(PlayerBase):
    pass
    

