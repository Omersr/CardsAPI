from http.client import HTTPException

import logging
logger = logging.getLogger("uvicorn.error")
from app.database_context import get_current_db
from app.models.action_cards import ActionCard
from app.models.item_card import ItemCard
from html import escape
from app.models.monster_card import MonsterCard
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
    
    