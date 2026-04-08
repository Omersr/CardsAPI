from http.client import HTTPException
from pathlib import Path
from PIL import Image

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