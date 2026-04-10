from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, Response, status
from fastapi.responses import HTMLResponse

from app.models.item_card import ItemCard
from app.schemas.item_card import ItemCardCreate, ItemCardOut, ItemCardUpdate
from app.utils.image_utils import download_card_image
from app.models.model_enums import DownloadType
router = APIRouter(prefix="/item-cards", tags=["item-cards"])
logger = logging.getLogger("uvicorn.error")


@router.post("/", response_model=ItemCardOut, status_code=status.HTTP_201_CREATED)
def create_item_card(payload: ItemCardCreate):
    try:
        return ItemCard.create(**payload.model_dump())
    except Exception as e:
        logger.error(f"Error creating ItemCard: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/", response_model=List[ItemCardOut])
def list_item_cards(
    used: Optional[bool] = None,
    monster_card_id: Optional[int] = None,
):
    try:
        items = ItemCard.get_all()

        if used is not None:
            items = [item for item in items if item.used == used]

        if monster_card_id is not None:
            items = [item for item in items if item.monster_card_id == monster_card_id]

        return items
    except Exception as e:
        logger.error(f"Error listing ItemCards: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/{item_card_id}", response_model=ItemCardOut)
def get_item_card(item_card_id: int):
    try:
        item = ItemCard.get_by_id(item_card_id)
        if not item:
            logger.error(f"ItemCard with id {item_card_id} not found.")
            return Response(status_code=404, content=f"ItemCard with id {item_card_id} not found.")
        return item
    except Exception as e:
        logger.error(f"Error retrieving ItemCard with id {item_card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.patch("/{item_card_id}", response_model=ItemCardOut)
def update_item_card(item_card_id: int, payload: ItemCardUpdate):
    try:
        update_data = payload.model_dump(exclude_unset=True)
        return ItemCard.update(item_id=item_card_id, **update_data)
    except Exception as e:
        logger.error(f"Error updating ItemCard with id {item_card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.delete("/{item_card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_card(item_card_id: int):
    try:
        ItemCard.delete(item_card_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting ItemCard with id {item_card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/display/{card_id:int}", response_class=HTMLResponse)
def render_item_card(card_id: int):
    try:
        return ItemCard.display_item_card(card_id)
    except Exception as e:
        logger.error(f"Error rendering ItemCard with id {card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))
    
@router.get("/download/{card_id:int}", response_class=HTMLResponse)
def download_item_card(card_id: int):
    try:
        if not ItemCard.get_by_id(card_id):
            logger.error(f"ItemCard with id {card_id} not found for download.")
            return Response(status_code=404, content=f"ItemCard with id {card_id} not found.")
        return download_card_image(card_id, DownloadType.item_card.value)
    except Exception as e:
        logger.error(f"Error rendering ItemCard with id {card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))