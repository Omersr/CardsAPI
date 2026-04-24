from __future__ import annotations

import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Response, status
from fastapi.responses import HTMLResponse
from app.models.monster_card import *
from app.models.model_enums import DownloadType
from app.schemas.monster_card import MonsterCardCreate, MonsterCardOut, MonsterCardUpdate
from app.services.battle_service import battle
from app.services.cards_service import display_monster_cards_possesions
from app.utils.image_utils import download_card_image

router = APIRouter(prefix="/monster-cards", tags=["monster-cards"])
logger = logging.getLogger("uvicorn.error")


@router.post("/", response_model=MonsterCardOut, status_code=status.HTTP_201_CREATED)
def create_monster_card(payload: MonsterCardCreate):
    try:
        return MonsterCard.create_card(payload)
    except Exception as e:
        logger.error(f"Error creating MonsterCard: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/", response_model=List[MonsterCardOut])
def list_monster_cards(
    limit: int = 20,
    offset: int = 0,
    primary_type: Optional[CardType] = None,
    secondary_type: Optional[CardType] = None,
    team: Optional[TeamType] = None,
    name_search: Optional[str] = None,
):
    try:
        return MonsterCard.list_cards(
            limit=limit,
            offset=offset,
            primary_type=primary_type,
            secondary_type=secondary_type,
            name_search=name_search,
        )
    except Exception as e:
        logger.error(f"Error listing MonsterCards: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/{card_id:int}", response_model=MonsterCardOut)
def get_monster_card(card_id: int):
    try:
        card = MonsterCard.get_card(card_id)
        if not card:
            logger.error(f"MonsterCard with id {card_id} not found.")
            return Response(status_code=404, content=f"MonsterCard with id {card_id} not found.")
        return card
    except Exception as e:
        logger.error(f"Error retrieving MonsterCard with id {card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/by-name/{name}", response_model=MonsterCardOut)
def get_monster_card_by_name(name: str):
    try:
        card = MonsterCard.get_card_by_name(name)
        if not card:
            logger.error(f"MonsterCard with name {name} not found.")
            return Response(status_code=404, content=f"MonsterCard with name {name} not found.")
        return card
    except Exception as e:
        logger.error(f"Error retrieving MonsterCard with name {name}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.patch("/{card_id:int}", response_model=MonsterCardOut)
def patch_monster_card(card_id: int, payload: MonsterCardUpdate):
    try:
        updates: Dict[str, Any] = payload.model_dump(exclude_unset=True)
        return MonsterCard.update_card(card_id, updates)
    except Exception as e:
        logger.error(f"Error updating MonsterCard with id {card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.delete("/{card_id:int}", status_code=status.HTTP_204_NO_CONTENT)
def remove_monster_card(card_id: int):
    try:
        MonsterCard.delete_card(card_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting MonsterCard with id {card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))


@router.get("/display/{card_id:int}", response_class=HTMLResponse)
def render_monster_card(card_id: int):
    try:
        return MonsterCard.display_monster_card(card_id)
    except Exception as e:
        logger.error(f"Error rendering MonsterCard with id {card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))

@router.get("/download/{card_id:int}", response_class=HTMLResponse)
def download_monster_card(card_id: int):
    try:
        if not MonsterCard.get_card(card_id):
            logger.error(f"MonsterCard with id {card_id} not found for download.")
            return Response(status_code=404, content=f"MonsterCard with id {card_id} not found.")
        return download_card_image(card_id, DownloadType.monster_card.value)
    except Exception as e:
        logger.error(f"Error rendering MonsterCard with id {card_id}: {str(e)}")
        return Response(status_code=500, content=str(e))

@router.post("/battle", status_code=status.HTTP_200_OK)
def monster_card_batte(payload: dict):
    try:
        if len(payload.get("card_ids", [])) != 2:
            logger.error("Exactly two card_ids must be provided for battle.")
            return Response(status_code=400, content="Exactly two card_ids must be provided for battle.")
        card1_id, card2_id = payload.get("card_ids")[0], payload.get("card_ids")[1]
        if not card1_id or not card2_id:
            logger.error("Both card1_id and card2_id are required.")
            return Response(status_code=400, content="Both card1_id and card2_id are required.")

        card1 = MonsterCard.get_card(card1_id)
        card2 = MonsterCard.get_card(card2_id)
        if not card1 or not card2:
            logger.error("One or both cards not found.")
            return Response(status_code=404, content="One or both cards not found.")

        winner_card = battle(card1, card2)
        return f"{winner_card.name} is the winner!"
    except Exception as e:
        logger.error(f"Error during MonsterCard battle: {str(e)}")
        return Response(status_code=500, content=str(e))

@router.get("/display_possesion", response_class=HTMLResponse)
def display_monster_cards_possesions_route(monster_card_ids: str):
    try:
        # "1,2,3" → [1,2,3]
        ids = [int(x) for x in monster_card_ids.split(",")]

        return display_monster_cards_possesions(ids)

    except Exception as e:
        logger.error(f"Error during display_possesion: {str(e)}")
        return Response(status_code=500, content=str(e))
    