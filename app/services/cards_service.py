import logging
logger = logging.getLogger("uvicorn.error")
from fastapi import HTTPException
from app.database_context import get_current_db
from app.models.action_cards import ActionCard
from app.models.item_card import ItemCard
from html import escape
from app.models.monster_card import MonsterCard
from app.models.model_enums import TeamType
from app.models.player import Player
from app.config import PUBLIC_TEAM_ICONS_URL
from sqlalchemy import select

def get_all_possessions(monster_card_id):
    action_cards = ActionCard.get_all_by_monster_card_id(monster_card_id)
    item_cards = ItemCard.get_all_by_monster_card_id(monster_card_id)
    return {
        "action_cards":action_cards,
        "item_cards":  item_cards
    }

def display_monster_cards_possesions(card_ids: list[int]) -> str:
        try:
            db = get_current_db()

            if not card_ids:
                raise HTTPException(status_code=400, detail="card_ids cannot be empty")

            sections = []

            for card_id in card_ids:
                monster = MonsterCard.get_card(card_id)
                if monster is None:
                    raise HTTPException(status_code=404, detail=f"Monster card id {card_id} not found")

                item_cards = db.execute(
                    select(ItemCard).where(ItemCard.monster_card_id == card_id)
                ).scalars().all()

                action_cards = db.execute(
                    select(ActionCard).where(ActionCard.monster_card_id == card_id)
                ).scalars().all()

                monster_html = MonsterCard.display_monster_card(card_id)
                escaped_monster_html = escape(monster_html, quote=True)

                item_cards_html = ""
                if item_cards:
                    for item in item_cards:
                        item_html = ItemCard.display_item_card(item.id)
                        item_cards_html += f"""
                        <iframe class="card-frame" srcdoc="{escape(item_html, quote=True)}"></iframe>
                        """
                else:
                    item_cards_html = "<p class='empty-msg'>No item cards found.</p>"

                action_cards_html = ""
                if action_cards:
                    for action in action_cards:
                        action_html = ActionCard.display_action_card(action.id)
                        action_cards_html += f"""
                        <iframe class="card-frame" srcdoc="{escape(action_html, quote=True)}"></iframe>
                        """
                else:
                    action_cards_html = "<p class='empty-msg'>No action cards found.</p>"

                section_html = f"""
                <section class="monster-section">
                    <h1 class="monster-title">{escape(monster.name)}</h1>

                    <div class="main-monster-card">
                        <iframe class="card-frame monster-frame" srcdoc="{escaped_monster_html}"></iframe>
                    </div>

                    <div class="sub-section">
                        <h2>Item Cards</h2>
                        <div class="cards-row">
                            {item_cards_html}
                        </div>
                    </div>

                    <div class="sub-section">
                        <h2>Action Cards</h2>
                        <div class="cards-row">
                            {action_cards_html}
                        </div>
                    </div>
                </section>
                """

                sections.append(section_html)

            return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Monster Possessions</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background: #f4f4f4;
                        margin: 0;
                        padding: 24px;
                    }}

                    .monster-section {{
                        background: white;
                        border-radius: 16px;
                        margin-bottom: 40px;
                        padding: 24px;
                        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
                    }}

                    .monster-title {{
                        margin: 0 0 20px 0;
                        font-size: 34px;
                        border-bottom: 3px solid #ddd;
                        padding-bottom: 10px;
                    }}

                    .sub-section {{
                        margin-top: 28px;
                    }}

                    .sub-section h2 {{
                        margin-bottom: 12px;
                        font-size: 24px;
                    }}

                    .cards-row {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 20px;
                        align-items: flex-start;
                    }}

                    .card-frame {{
                        width: 280px;
                        height: 500px;
                        border: none;
                        background: transparent;
                        overflow: hidden;
                    }}

                    .monster-frame {{
                        width: 280px;
                        height: 500px;
                    }}

                    .empty-msg {{
                        color: #666;
                        font-style: italic;
                    }}
                </style>
            </head>
            <body>
                {''.join(sections)}
            </body>
            </html>
            """

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


def display_alive_team_monster_cards() -> str:
        try:
            db = get_current_db()

            stmt = (
                select(MonsterCard, Player)
                .outerjoin(Player, Player.monster_card_id == MonsterCard.id)
                .where(MonsterCard.alive.is_(True))
                .where(MonsterCard.team.is_not(None))
                .where(MonsterCard.team != TeamType.neutral)
                .order_by(MonsterCard.team, Player.name, MonsterCard.name)
            )

            team_cards: dict[TeamType, list[tuple[MonsterCard, Player | None]]] = {
                team: [] for team in TeamType if team != TeamType.neutral
            }

            for monster, player in db.execute(stmt).all():
                if monster.team in team_cards:
                    team_cards[monster.team].append((monster, player))

            team_sections = []

            for team, card_rows in team_cards.items():
                team_label = team.value.capitalize()
                team_icon_path = f"{PUBLIC_TEAM_ICONS_URL}/{team.value}_team_banner.png"

                if card_rows:
                    cards_html = ""
                    for monster, player in card_rows:
                        monster_html = MonsterCard.display_monster_card(monster.id)
                        player_name = player.name if player is not None else "No player assigned"
                        cards_html += f"""
                        <article class="player-card">
                            <h3 class="player-name">{escape(player_name)}</h3>
                            <iframe class="card-frame" srcdoc="{escape(monster_html, quote=True)}"></iframe>
                        </article>
                        """
                else:
                    cards_html = "<p class='empty-msg'>No alive monster cards for this team.</p>"

                team_sections.append(f"""
                <section class="team-section team-{escape(team.value)}">
                    <div class="team-header">
                        <img class="team-logo" src="{escape(team_icon_path, quote=True)}" alt="{escape(team_label)} team logo">
                        <h2>{escape(team_label)} Team</h2>
                    </div>
                    <div class="cards-grid">
                        {cards_html}
                    </div>
                </section>
                """)

            return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Alive Team Monster Cards</title>
                <style>
                    * {{
                        box-sizing: border-box;
                    }}

                    body {{
                        font-family: Arial, sans-serif;
                        background: linear-gradient(135deg, #edf7f1 0%, #fff7ea 46%, #edf5fb 100%);
                        margin: 0;
                        min-height: 100vh;
                        padding: 24px;
                        color: #18202a;
                    }}

                    .page-title {{
                        margin: 0 0 28px 0;
                        font-size: 38px;
                        line-height: 1.1;
                        color: #111827;
                    }}

                    .team-section {{
                        border-radius: 18px;
                        margin-bottom: 34px;
                        padding: 20px;
                        box-shadow: 0 12px 28px rgba(24, 32, 42, 0.12);
                        border: 1px solid rgba(255, 255, 255, 0.7);
                    }}

                    .team-bull {{
                        background: linear-gradient(135deg, #dff3df 0%, #79bd86 48%, #287747 100%);
                    }}

                    .team-owl {{
                        background: linear-gradient(135deg, #ffe1dc 0%, #d44434 48%, #8e100d 100%);
                    }}

                    .team-swordfish {{
                        background: linear-gradient(135deg, #e1f5ff 0%, #4b9bc6 48%, #145a89 100%);
                    }}

                    .team-header {{
                        display: flex;
                        align-items: center;
                        gap: 18px;
                        margin-bottom: 20px;
                        padding-bottom: 16px;
                        border-bottom: 2px solid rgba(255, 255, 255, 0.38);
                    }}

                    .team-logo {{
                        width: 172px;
                        max-width: 42vw;
                        height: 72px;
                        object-fit: contain;
                        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.18));
                    }}

                    .team-header h2 {{
                        margin: 0;
                        font-size: 30px;
                        color: #ffffff;
                        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.32);
                    }}

                    .cards-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(232px, 240px));
                        justify-content: center;
                        max-width: calc(7 * 240px + 6 * 18px);
                        margin: 0 auto;
                        gap: 18px;
                        align-items: start;
                    }}

                    .player-card {{
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        gap: 12px;
                        width: 240px;
                        padding: 14px 10px 16px;
                        border-radius: 14px;
                        background: rgba(255, 255, 255, 0.78);
                        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.7);
                    }}

                    .player-name {{
                        margin: 0;
                        width: 100%;
                        min-height: 34px;
                        padding: 7px 10px;
                        border-radius: 999px;
                        background: #18202a;
                        color: #ffffff;
                        font-size: 18px;
                        line-height: 1.1;
                        text-align: center;
                        overflow-wrap: anywhere;
                    }}

                    .card-frame {{
                        width: 280px;
                        height: 500px;
                        border: none;
                        background: transparent;
                        overflow: hidden;
                    }}

                    .player-card .card-frame {{
                        transform: scale(0.84);
                        transform-origin: top center;
                        margin-bottom: -80px;
                    }}

                    .empty-msg {{
                        margin: 6px 0 0;
                        color: #4b5563;
                        font-style: italic;
                    }}

                    @media (max-width: 640px) {{
                        body {{
                            padding: 16px;
                        }}

                        .page-title {{
                            font-size: 30px;
                        }}

                        .team-header {{
                            align-items: flex-start;
                            flex-direction: column;
                            gap: 10px;
                        }}

                        .team-header h2 {{
                            font-size: 26px;
                        }}

                        .cards-grid {{
                            grid-template-columns: 1fr;
                            justify-items: center;
                        }}
                    }}
                </style>
            </head>
            <body>
                <h1 class="page-title">Alive Team Monster Cards</h1>
                {''.join(team_sections)}
            </body>
            </html>
            """

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    
