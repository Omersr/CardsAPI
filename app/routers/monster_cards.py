from __future__ import annotations

from typing import List, Optional, Annotated, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.deps import get_db

from app.database import SessionLocal
from app.models.monster_card import CardType, DisplayType
from app.schemas.monster_card import MonsterCardCreate, MonsterCardOut
from app.crud.monster_card import *
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/monster-cards", tags=["monster-cards"])



DbSession = Annotated[Session, Depends(get_db)]


# --- Update schema (all fields optional for PATCH) ---
class MonsterCardUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    primary_type: Optional[CardType] = None
    secondary_type: Optional[CardType] = None
    health: Optional[int] = Field(None, ge=0)
    attack: Optional[int] = Field(None, ge=0)
    defense: Optional[int] = Field(None, ge=0)
    speed: Optional[int] = Field(None, ge=0)


# --- Endpoints ---

@router.post("/", response_model=MonsterCardOut, status_code=status.HTTP_201_CREATED)
def create_monster_card(payload: MonsterCardCreate, db: DbSession):
    try:
        return create_card(db, payload)
    except DuplicateNameError as e:
        # 409 Conflict for unique violation
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/", response_model=List[MonsterCardOut])
def list_monster_cards(
    db: DbSession,
    limit: int = 20,
    offset: int = 0,
    primary_type: Optional[CardType] = None,
    secondary_type: Optional[CardType] = None,
    name_search: Optional[str] = None,
):
    return list_cards(
        db,
        limit=limit,
        offset=offset,
        primary_type=primary_type,
        secondary_type=secondary_type,
        name_search=name_search,
    )


@router.get("/{card_id:int}", response_model=MonsterCardOut)
def get_monster_card(card_id: int, db: DbSession):
    card = get_card(db, card_id)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found.")
    return card


    

@router.get("/by-name/{name}", response_model=MonsterCardOut)
def get_monster_card_by_name(name: str, db: DbSession):
    card = get_card_by_name(db, name)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found.")
    return card




@router.patch("/{card_id:int}", response_model=MonsterCardOut)
def patch_monster_card(card_id: int, payload: MonsterCardUpdate, db: DbSession):
    updates: Dict[str, Any] = payload.model_dump(exclude_unset=True)
    try:
        return update_card(db, card_id, updates)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateNameError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{card_id:int}", status_code=status.HTTP_204_NO_CONTENT)
def remove_monster_card(card_id: int, db: DbSession):
    try:
        delete_card(db, card_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/display/normal/{card_id:int}",response_class=HTMLResponse)
def display_normal_monster_card(card_id: int, db: DbSession):
    try:
        return display_monster_card(db,card_id, DisplayType.normal)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.get("/display/sunlight/{card_id:int}",response_class=HTMLResponse)
def display_normal_monster_card(card_id: int, db: DbSession):
    try:
        return display_monster_card(db,card_id, DisplayType.sunlight)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.get("/display/moonlight/{card_id:int}",response_class=HTMLResponse)
def display_normal_monster_card(card_id: int, db: DbSession):
    try:
        return display_monster_card(db,card_id, DisplayType.moonlight)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.get("/display/twilight/{card_id:int}",response_class=HTMLResponse)
def display_normal_monster_card(card_id: int, db: DbSession):
    try:
        return display_monster_card(db,card_id, DisplayType.twilight)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))