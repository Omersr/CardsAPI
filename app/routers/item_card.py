from __future__ import annotations

from http.client import HTTPException
from typing import List, Optional

from fastapi import APIRouter, Response, status

from app.exceptions import NotFoundError
from app.models.item_card import ItemCard
from app.schemas.item_card import ItemCardCreate, ItemCardOut, ItemCardUpdate
from fastapi.responses import HTMLResponse
router = APIRouter(prefix="/item-cards", tags=["item-cards"])


@router.post("/", response_model=ItemCardOut, status_code=status.HTTP_201_CREATED)
def create_item_card(payload: ItemCardCreate):
    return ItemCard.create(**payload.model_dump())


@router.get("/", response_model=List[ItemCardOut])
def list_item_cards(
    used: Optional[bool] = None,
    monster_card_id: Optional[int] = None,
):
    items = ItemCard.get_all()

    if used is not None:
        items = [item for item in items if item.used == used]

    if monster_card_id is not None:
        items = [item for item in items if item.monster_card_id == monster_card_id]

    return items


@router.get("/{item_card_id}", response_model=ItemCardOut)
def get_item_card(item_card_id: int):
    return ItemCard.get_by_id(item_card_id)


@router.patch("/{item_card_id}", response_model=ItemCardOut)
def update_item_card(item_card_id: int, payload: ItemCardUpdate):
    update_data = payload.model_dump(exclude_unset=True)
    return ItemCard.update(item_id=item_card_id, **update_data)


@router.delete("/{item_card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_card(item_card_id: int):
    ItemCard.delete(item_card_id)
    return Response(status_code=status.HTTP_200_OK)

@router.get("/display/{card_id:int}",response_class=HTMLResponse)
def render_monster_card(card_id: int):
    try:
        return ItemCard.display_item_card(card_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))