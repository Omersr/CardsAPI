from pathlib import Path
from PIL import Image
from http.client import HTTPException
from playwright.sync_api import sync_playwright
import logging
from app.models.model_enums import DownloadType
logger = logging.getLogger("uvicorn.error")
def ensure_image_size(image_path: Path, target_size: tuple[int, int] = (230, 150)) -> None:
        if not image_path.exists():
            return

        try:
            with Image.open(image_path) as img:
                if img.size != target_size:
                    resized = img.resize(target_size, Image.Resampling.LANCZOS)
                    resized.save(image_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not process image {image_path}: {e}")

def download_card_image(card_id ,card_type: str):
    sub_folder = "monster_cards" if card_type == DownloadType.monster_card.value else "power_up_cards"
    output_path = Path(f"assets/{sub_folder}/full_card_images/{card_type}-{card_id}.png")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"http://127.0.0.1:8000/{card_type}/display/{card_id}", wait_until="networkidle")
            card = page.locator(".card")
            card.screenshot(path=output_path, omit_background=True)
            browser.close()
        logger.info(f"Successfully converted HTML to image: {output_path}")
        return output_path
    except Exception as e:
        logger.info(f"Failed to convert HTML to image: {e}")
        raise e