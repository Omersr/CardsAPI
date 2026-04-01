from __future__ import annotations
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Response, status
from app.models.monster_card import *
from app.schemas.monster_card import MonsterCardCreate, MonsterCardOut, MonsterCardUpdate
from fastapi.responses import HTMLResponse
from app.exceptions import *
from app.services.battle_service import battle
router = APIRouter(prefix="/monster-cards", tags=["monster-cards"])


@router.post("/", response_model=MonsterCardOut, status_code=status.HTTP_201_CREATED)
def create_monster_card(payload: MonsterCardCreate):
    try:
        return MonsterCard.create_card(payload)
    except DuplicateNameError as e:
        # 409 Conflict for unique violation
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.get("/", response_model=List[MonsterCardOut])
def list_monster_cards(
    limit: int = 20,
    offset: int = 0,
    primary_type: Optional[CardType] = None,
    secondary_type: Optional[CardType] = None,
    team: Optional[TeamType] = None,
    name_search: Optional[str] = None,
):
    return MonsterCard.list_cards(
        limit=limit,
        offset=offset,
        primary_type=primary_type,
        secondary_type=secondary_type,
        name_search=name_search,
    )


@router.get("/{card_id:int}", response_model=MonsterCardOut)
def get_monster_card(card_id: int):
    card = MonsterCard.get_card(card_id)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found.")
    return card


    

@router.get("/by-name/{name}", response_model=MonsterCardOut)
def get_monster_card_by_name(name: str):
    card = MonsterCard.get_card_by_name(name)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found.")
    return card




@router.patch("/{card_id:int}", response_model=MonsterCardOut)
def patch_monster_card(card_id: int, payload: MonsterCardUpdate):
    updates: Dict[str, Any] = payload.model_dump(exclude_unset=True)
    try:
        return MonsterCard.update_card(card_id, updates)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateNameError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{card_id:int}", status_code=status.HTTP_204_NO_CONTENT)
def remove_monster_card(card_id: int):
    try:
        MonsterCard.delete_card(card_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/display/{card_id:int}",response_class=HTMLResponse)
def render_monster_card(card_id: int):
    try:
        return MonsterCard.display_monster_card(card_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/battle", status_code=status.HTTP_200_OK)
def monster_card_batte(payload: dict):
    try:
        card1_id = payload.get("card1_id")
        card2_id = payload.get("card2_id")
        if not card1_id or not card2_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Both card1_id and card2_id are required.")
        card1 = MonsterCard.get_card(card1_id)
        card2 = MonsterCard.get_card(card2_id)
        if not card1 or not card2:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both cards not found.")
        winner_card = battle(card1, card2)
        return f"{winner_card.name} is the winner!"
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))