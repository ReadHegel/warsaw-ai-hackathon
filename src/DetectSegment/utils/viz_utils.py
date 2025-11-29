from typing import List, Dict, Any
from PIL import Image, ImageDraw
import numpy as np


def draw_boxes(image: Image.Image, boxes: List[Dict[str, Any]], color: str = "red") -> Image.Image:
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    for det in boxes:
        b = det["box"]
        draw.rectangle([b["xmin"], b["ymin"], b["xmax"], b["ymax"]], outline=color, width=3)
        label = det.get("label", "")
        score = det.get("score", None)
        text = label if score is None else f"{label} ({score:.2f})"
        if text:
            draw.text((b["xmin"] + 3, b["ymin"] + 3), text, fill=color)
    return img_copy


def overlay_mask(image: Image.Image, mask: np.ndarray, color=(0, 255, 0), alpha: float = 0.5) -> Image.Image:
    base = np.array(image).astype(np.float32)
    overlay = np.zeros_like(base)
    overlay[mask.astype(bool)] = color
    blended = (base * (1 - alpha) + overlay * alpha).astype(np.uint8)
    return Image.fromarray(blended)
