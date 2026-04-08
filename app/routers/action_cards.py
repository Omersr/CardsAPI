from __future__ import annotations

from http.client import HTTPException
from typing import List, Optional

from fastapi import APIRouter, Response, status
from fastapi.responses import HTMLResponse

from app.exceptions import NotFoundError
from app.models.action_cards import ActionCard
from app.schemas.action_cards import ActionCardCreate, ActionCardOut, ActionCardUpdate

router = APIRouter(prefix="/action-cards", tags=["action-cards"])


@router.post("/", response_model=ActionCardOut, status_code=status.HTTP_201_CREATED)
def create_action_card(payload: ActionCardCreate):
    return ActionCard.create(**payload.model_dump())


@router.get("/", response_model=List[ActionCardOut])
def list_action_cards(
    limit: int = 20,
    offset: int = 0,
    used: Optional[bool] = None,
    monster_card_id: Optional[int] = None,
    name_search: Optional[str] = None,
):
    return ActionCard.get_all(
        limit=limit,
        offset=offset,
        used=used,
        monster_card_id=monster_card_id,
        name_search=name_search,
    )


@router.get("/{action_card_id}", response_model=ActionCardOut)
def get_action_card(action_card_id: int):
    return ActionCard.get_by_id(action_card_id)


@router.patch("/{action_card_id}", response_model=ActionCardOut)
def update_action_card(action_card_id: int, payload: ActionCardUpdate):
    return ActionCard.update(
        action_card_id=action_card_id,
        **payload.model_dump(exclude_unset=True)
    )


@router.delete("/{action_card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action_card(action_card_id: int):
    ActionCard.delete(action_card_id)
    return Response(status_code=status.HTTP_200_OK)

@router.get("/display/{card_id:int}",response_class=HTMLResponse)
def render_action_card(card_id: int):
    try:
        return ActionCard.display_action_card(card_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))