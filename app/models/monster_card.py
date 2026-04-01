from __future__ import annotations
from pathlib import Path
from string import Template
from typing import Optional, Any

from fastapi import HTTPException
from PIL import Image
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Enum as PgEnum,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    select,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column
from .model_enums import CardType, RarityType, TeamType
from app.config import (
    HTML_FORMATS_DIR,
    MONSTER_CARD_IMAGES_DIR,
    PUBLIC_MONSTER_IMAGES_URL,
    PUBLIC_TEAM_ICONS_URL,
    PUBLIC_TYPE_ICONS_URL,
)
from app.database import Base
from app.models.type_effectiveness import TypeEffectiveness
from app.schemas.monster_card import MonsterCardCreate
from app.database_context import get_current_db


class MonsterCard(Base):
    __tablename__ = "monster_cards"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    primary_type: Mapped[CardType] = mapped_column(
        PgEnum(CardType, name="card_type_enum", create_type=True, native_enum=True),
        nullable=False,
        index=True,
    )
    secondary_type: Mapped[Optional[CardType]] = mapped_column(
        PgEnum(CardType, name="card_type_enum", create_type=False, native_enum=True),
        nullable=True,
        index=True,
    )
    team: Mapped[Optional[TeamType]] = mapped_column(
        PgEnum(TeamType, name="team_type_enum", create_type=False, native_enum=True),
        nullable=True,
        default=TeamType.neutral,
        index=True,
    )
    rarity: Mapped[Optional[RarityType]] = mapped_column(
        PgEnum(RarityType, name="rarity_type_enum", create_type=False, native_enum=True),
        nullable=True,
        default=RarityType.normal,
    )

    health: Mapped[int] = mapped_column(Integer, nullable=False)
    attack: Mapped[int] = mapped_column(Integer, nullable=False)
    defense: Mapped[int] = mapped_column(Integer, nullable=False)
    speed: Mapped[int] = mapped_column(Integer, nullable=False)
    alive: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)

    __table_args__ = (
        UniqueConstraint("name", name="uq_monster_cards_name"),
        CheckConstraint("health >= 0", name="ck_monster_cards_health_nonneg"),
        CheckConstraint("attack >= 0", name="ck_monster_cards_attack_nonneg"),
        CheckConstraint("defense >= 0", name="ck_monster_cards_defense_nonneg"),
        CheckConstraint("speed >= 0", name="ck_monster_cards_speed_nonneg"),
        Index("ix_monster_cards_types", "primary_type", "secondary_type"),
    )

    _UPDATABLE_FIELDS = {
        "name",
        "description",
        "primary_type",
        "secondary_type",
        "health",
        "attack",
        "defense",
        "speed",
        "team",
        "rarity",
        "alive",
    }

    RARITY_TO_TEMPLATE = {
        RarityType.normal: "normal_card.html",
        RarityType.sunlight: "sunlight_card.html",
        RarityType.moonlight: "moonlight_card.html",
        RarityType.twilight: "twilight_card.html",
    }

    @staticmethod
    def _ensure_image_size(image_path: Path, target_size: tuple[int, int] = (230, 150)) -> None:
        if not image_path.exists():
            return

        try:
            with Image.open(image_path) as img:
                if img.size != target_size:
                    resized = img.resize(target_size, Image.Resampling.LANCZOS)
                    resized.save(image_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not process image {image_path}: {e}")

    @staticmethod
    def create_card(data: MonsterCardCreate) -> "MonsterCard":
        db = get_current_db()
        secondary = data.secondary_type or data.primary_type

        card = MonsterCard(
            name=data.name,
            description=data.description,
            primary_type=data.primary_type,
            secondary_type=secondary,
            health=data.health,
            attack=data.attack,
            defense=data.defense,
            speed=data.speed,
            team=data.team,
            rarity=data.rarity,
            alive=data.alive,
        )

        db.add(card)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to create card: {e.orig}") from e

        db.refresh(card)
        return card

    @staticmethod
    def get_card(card_id: int) -> Optional["MonsterCard"]:
        db = get_current_db()
        stmt = select(MonsterCard).where(MonsterCard.id == card_id)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_card_by_name(name: str) -> Optional["MonsterCard"]:
        db = get_current_db()
        stmt = select(MonsterCard).where(MonsterCard.name == name)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_cards(
        *,
        limit: int = 20,
        offset: int = 0,
        primary_type: Optional[CardType] = None,
        secondary_type: Optional[CardType] = None,
        team: Optional[TeamType] = None,
        name_search: Optional[str] = None,
    ) -> list["MonsterCard"]:
        db = get_current_db()
        stmt = select(MonsterCard).order_by(MonsterCard.id).limit(limit).offset(offset)

        if team is not None:
            stmt = stmt.where(MonsterCard.team == team)
        if primary_type is not None:
            stmt = stmt.where(MonsterCard.primary_type == primary_type)
        if secondary_type is not None:
            stmt = stmt.where(MonsterCard.secondary_type == secondary_type)
        if name_search:
            stmt = stmt.where(MonsterCard.name.ilike(f"%{name_search}%"))

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def update_card(card_id: int, updates: dict[str, Any]) -> "MonsterCard":
        db = get_current_db()
        card = MonsterCard.get_card(card_id)
        if card is None:
            raise HTTPException(status_code=404, detail=f"Card id {card_id} not found")

        clean = {k: v for k, v in updates.items() if k in MonsterCard._UPDATABLE_FIELDS}

        for field, value in clean.items():
            setattr(card, field, value)

        if "primary_type" in clean and ("secondary_type" not in clean or clean.get("secondary_type") is None):
            card.secondary_type = card.primary_type

        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to update card: {e.orig}") from e

        db.refresh(card)
        return card

    @staticmethod
    def delete_card(card_id: int) -> None:
        db = get_current_db()
        card = MonsterCard.get_card(card_id)
        if card is None:
            raise HTTPException(status_code=404, detail=f"Card id {card_id} not found")

        db.delete(card)
        db.commit()

    @staticmethod
    def display_monster_card(card_id: int) -> str:
        card = MonsterCard.get_card(card_id)
        if card is None:
            raise HTTPException(status_code=404, detail=f"Card id {card_id} not found")

        rarity = card.rarity or RarityType.normal
        template_name = MonsterCard.RARITY_TO_TEMPLATE[rarity]
        html_display_path = HTML_FORMATS_DIR / template_name
        raw_html = html_display_path.read_text(encoding="utf-8")

        monster_filename = f"{card.name.capitalize().replace(' ', '_')}.png"
        MonsterCard._ensure_image_size(MONSTER_CARD_IMAGES_DIR / monster_filename)

        image_path = f"{PUBLIC_MONSTER_IMAGES_URL}/{monster_filename}"
        primary_type_image_path = f"{PUBLIC_TYPE_ICONS_URL}/{card.primary_type.value}_icon.png"
        secondary_type_image_path = f"{PUBLIC_TYPE_ICONS_URL}/{card.secondary_type.value}_icon.png"

        team_value = card.team.value if card.team is not None else TeamType.neutral.value

        team_icon_path = f"{PUBLIC_TEAM_ICONS_URL}/{team_value}_team_banner.png"
        decoration_left = f"{PUBLIC_TEAM_ICONS_URL}/banner_decoration_left.png"
        decoration_right = f"{PUBLIC_TEAM_ICONS_URL}/banner_decoration_right.png"

        if card.team == TeamType.neutral:
            team_icon_path = f"{PUBLIC_TEAM_ICONS_URL}/{team_value}_monster_banner.png"
            decoration_left = f"{PUBLIC_TEAM_ICONS_URL}/neutral_banner_decoration_left.png"
            decoration_right = f"{PUBLIC_TEAM_ICONS_URL}/neutral_banner_decoration_right.png"

        template = Template(raw_html)
        output_html = template.safe_substitute(
            name=card.name,
            description=card.description or "",
            primary_type_image_path=primary_type_image_path,
            secondary_type_image_path=secondary_type_image_path,
            health=card.health,
            attack=card.attack,
            defense=card.defense,
            speed=card.speed,
            image_path=image_path,
            team_icon_path=team_icon_path,
            decoration_right=decoration_right,
            decoration_left=decoration_left,
        )
        return output_html

    @staticmethod
    def get_damage_multipliers(
        first_monster_card: "MonsterCard",
        second_monster_card: "MonsterCard",
    ) -> tuple[float, float]:
        first_multiplier = 1.0
        second_multiplier = 1.0

        first_attack_types = [first_monster_card.primary_type]
        if first_monster_card.secondary_type is not None:
            first_attack_types.append(first_monster_card.secondary_type)

        second_defense_types = [second_monster_card.primary_type]
        if second_monster_card.secondary_type is not None:
            second_defense_types.append(second_monster_card.secondary_type)

        for attacker_type in first_attack_types:
            for defender_type in second_defense_types:
                if TypeEffectiveness.is_effective(attacker_type, defender_type):
                    first_multiplier *= 2
                else:
                    first_multiplier *= 0.5

        second_attack_types = [second_monster_card.primary_type]
        if second_monster_card.secondary_type is not None:
            second_attack_types.append(second_monster_card.secondary_type)

        first_defense_types = [first_monster_card.primary_type]
        if first_monster_card.secondary_type is not None:
            first_defense_types.append(first_monster_card.secondary_type)

        for attacker_type in second_attack_types:
            for defender_type in first_defense_types:
                if TypeEffectiveness.is_effective(attacker_type, defender_type):
                    second_multiplier *= 2
                else:
                    second_multiplier *= 0.5

        return first_multiplier, second_multiplier