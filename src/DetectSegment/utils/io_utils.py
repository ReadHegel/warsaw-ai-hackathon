from typing import Any, Dict
import json
from pathlib import Path
from PIL import Image


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Dict[str, Any]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_image(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")


def save_image(path: str, image: Image.Image) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
