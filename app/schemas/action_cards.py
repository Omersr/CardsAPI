from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class ActionCardBase(BaseModel):
    name: str
    description: str
    monster_card_id: int
    used: bool = False


class ActionCardCreate(ActionCardBase):
    pass


class ActionCardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    monster_card_id: Optional[int] = None
    used: Optional[bool] = None


class ActionCardOut(ActionCardBase):
    id: int

    model_config = ConfigDict(from_attributes=True)