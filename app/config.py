from pathlib import Path

# 1. Absolute project root (CardsAPI/)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Absolute path on disk to /assets
ASSETS_DIR = BASE_DIR / "assets"

# 3. Absolute path on disk to monster card assets
ASSETS_MONSTER_DIR = ASSETS_DIR / "monster_cards"

# 3a. Absolute path (used by Python to open the HTML template files)
HTML_FORMATS_DIR = ASSETS_MONSTER_DIR / "card_templates"

# 3b. Absolute paths (optional, useful for debugging/exists())
MONSTER_CARD_IMAGES_DIR = ASSETS_MONSTER_DIR / "monster_card_images"
TYPES_ICONS_DIR = ASSETS_MONSTER_DIR / "type_icons"

# 4. Public URLs for browser (these go into the HTML you return)
PUBLIC_ASSETS_BASE_URL = "/assets"  # you mounted this in main.py

PUBLIC_MONSTER_IMAGES_URL = f"{PUBLIC_ASSETS_BASE_URL}/monster_cards/monster_card_images"
PUBLIC_TYPE_ICONS_URL = f"{PUBLIC_ASSETS_BASE_URL}/monster_cards/types_icons"
PUBLIC_TEAM_ICONS_URL = f"{PUBLIC_ASSETS_BASE_URL}/team_icons/"
