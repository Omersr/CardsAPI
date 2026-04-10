from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, Response, status
from fastapi.responses import HTMLResponse

from app.models.action_cards import ActionCard
from app.models.model_enums import DownloadType
from app.schemas.action_cards import ActionCardCreate, ActionCardOut, ActionCardUpdate
from app.utils.image_utils import download_card_image

router = APIRouter(prefix="/action-cards", tags=["action-cards"])
logger = logging.getLogger("uvicorn.error")


@router.post("/", response_model=ActionCardOut, status_code=status.HTTP_201_CREATED)
def create_action_card(payload: ActionCardCreate):
    try:
        return ActionCard.create(**payload.model_dump())
    except Exception as e:
        logger.error(f"Error creating ActionCard: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/", response_model=List[ActionCardOut])
def list_action_cards(
    limit: int = 20,
    offset: int = 0,
    used: Optional[bool] = None,
    monster_card_id: Optional[int] = None,
    name_search: Optional[str] = None,
):
    try:
        return ActionCard.get_all(
            limit=limit,
            offset=offset,
            used=used,
            monster_card_id=monster_card_id,
            name_search=name_search,
        )
    except Exception as e:
        logger.error(f"Error listing ActionCards: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/{action_card_id}", response_model=ActionCardOut)
def get_action_card(action_card_id: int):
    try:
        card = ActionCard.get_by_id(action_card_id)
        if not card:
            logger.error(f"ActionCard with id {action_card_id} not found.")
            return Response(status_code=404, content=f"ActionCard with id {action_card_id} not found.")
        return card
    except Exception as e:
        logger.error(f"Error retrieving ActionCard with id {action_card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.patch("/{action_card_id}", response_model=ActionCardOut)
def update_action_card(action_card_id: int, payload: ActionCardUpdate):
    try:
        return ActionCard.update(
            action_card_id=action_card_id,
            **payload.model_dump(exclude_unset=True)
        )
    except Exception as e:
        logger.error(f"Error updating ActionCard with id {action_card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.delete("/{action_card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action_card(action_card_id: int):
    try:
        ActionCard.delete(action_card_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting ActionCard with id {action_card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/display/{card_id:int}", response_class=HTMLResponse)
def render_action_card(card_id: int):
    try:
        return ActionCard.display_action_card(card_id)
    except Exception as e:
        logger.error(f"Error rendering ActionCard with id {card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))

@router.get("/download/{card_id:int}", response_class=HTMLResponse)
def download_item_card(card_id: int):
    try:
        if not ActionCard.get_by_id(card_id):
            logger.error(f"ItemCard with id {card_id} not found for download.")
            return Response(status_code=404, content=f"ItemCard with id {card_id} not found.")
        return download_card_image(card_id, DownloadType.action_card.value)
    except Exception as e:
        logger.error(f"Error rendering ItemCard with id {card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))