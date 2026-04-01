from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class ItemCardBase(BaseModel):
    name: str
    description: str
    monster_card_id: int
    used: bool = False


class ItemCardCreate(ItemCardBase):
    pass


class ItemCardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    monster_card_id: Optional[int] = None
    used: Optional[bool] = None


class ItemCardOut(ItemCardBase):
    id: int

    model_config = ConfigDict(from_attributes=True)