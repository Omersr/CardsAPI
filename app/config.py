from pathlib import Path

# Absolute project root (CardsAPI/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Absolute path on disk to /assets
ASSETS_DIR = BASE_DIR / "assets"

# Absolute paths on disk
ASSETS_MONSTER_DIR = ASSETS_DIR / "monster_cards"
ASSETS_POWER_UP_DIR = ASSETS_DIR / "power_up_cards"

# HTML templates on disk
HTML_FORMATS_DIR = ASSETS_MONSTER_DIR / "card_templates"
HTML_ITEM_CARD_TEMPLATE = ASSETS_POWER_UP_DIR / "power_up_templates" / "item_card.html"
HTML_ACTION_CARD_TEMPLATE = ASSETS_POWER_UP_DIR / "power_up_templates" / "action_card.html"

# Image directories on disk
MONSTER_CARD_IMAGES_DIR = ASSETS_MONSTER_DIR / "monster_card_images"
TEAM_STATE_IMAGES_DIR = ASSETS_MONSTER_DIR / "team_state_images"
TYPES_ICONS_DIR = ASSETS_MONSTER_DIR / "type_icons"
ITEM_CARD_IMAGES_DIR = ASSETS_POWER_UP_DIR / "items_images"

# Public URLs for browser
PUBLIC_ASSETS_BASE_URL = "/assets"

PUBLIC_MONSTER_IMAGES_URL = f"{PUBLIC_ASSETS_BASE_URL}/monster_cards/monster_card_images"
PUBLIC_TYPE_ICONS_URL = f"{PUBLIC_ASSETS_BASE_URL}/monster_cards/types_icons"
PUBLIC_TEAM_ICONS_URL = f"{PUBLIC_ASSETS_BASE_URL}/team_icons"

PUBLIC_POWERUP_CARDS_URL = f"{PUBLIC_ASSETS_BASE_URL}/power_up_cards"
PUBLIC_ITEM_CARD_IMAGES_URL = f"{PUBLIC_POWERUP_CARDS_URL}/items_images"

ACTION_CARD_IMAGES_DIR = ASSETS_POWER_UP_DIR / "action_images"
PUBLIC_ACTION_CARD_IMAGES_URL = f"{PUBLIC_POWERUP_CARDS_URL}/action_images"
