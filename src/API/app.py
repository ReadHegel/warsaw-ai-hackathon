from typing import List, Dict, Any
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from DetectSegment.pipelines.detect_and_segment import DetectAndSegmentPipeline
from DetectSegment.utils.io_utils import load_image

# Optional simple chat module from UserPromptProcess
try:
    from UserPromptProcess.chat import generate_chat_answer
except Exception:
    def generate_chat_answer(chat_history: List[Dict[str, Any]], classes: List[str]) -> str:
        last_user = ""
        for msg in reversed(chat_history or []):
            if msg.get("role") == "user":
                last_user = msg.get("content", "")
                break
        return f"Detected classes: {', '.join(classes)}. Your last message: {last_user}"

device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Using device: {device}")

model = Sam3Model.from_pretrained("facebook/sam3").to(device)
processor = Sam3Processor.from_pretrained("facebook/sam3")
model.eval()

ASSETS_DIR = Path("src/images")
OUTPUTS_DIR = Path("src/DetectSegment/tests/outputs_api")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

SAM_CHECKPOINT = os.environ.get("SAM_CHECKPOINT")
if not SAM_CHECKPOINT:
    # Reuse tests checkpoint auto download if present
    checkpoints_dir = Path("src/DetectSegment/tests/checkpoints")
    try:
        from DetectSegment.tests.test_run import download_random_checkpoint
        SAM_CHECKPOINT = download_random_checkpoint(checkpoints_dir)
    except Exception:
        SAM_CHECKPOINT = None


app = FastAPI(title="DetectSegment API")


class SegmentImageRequest(BaseModel):
    chat_history: List[Dict[str, Any]]
    classes: List[str]


def build_pipeline() -> DetectAndSegmentPipeline:
    if not SAM_CHECKPOINT:
        raise RuntimeError("SAM checkpoint not available. Set SAM_CHECKPOINT env or place in tests/checkpoints.")
    # Infer type from filename suffix
    inferred_type = "vit_h"
    for t in ["vit_h", "vit_l", "vit_b"]:
        if str(SAM_CHECKPOINT).endswith(f"{t}.pth"):
            inferred_type = t
            break
    return DetectAndSegmentPipeline(
        detector_model="google/owlvit-base-patch32",
        sam_checkpoint=SAM_CHECKPOINT,
        sam_model_type=inferred_type,
        confidence_threshold=0.25,
    )

def process_image_with_class_list(image: Image.Image, class_names: List[str],
                              score_threshold: float = 0.5,
                              mask_threshold: float = 0.5):
    for class_name in class_names:
        res = predict_for_class(image, class_name)
        if len(res["masks"]) == 0:
            continue
        # res["masks"] is [N, H, W] tensor; extend as individual masks
        all_masks.extend(list(res["masks"]))
        all_labels.extend([class_name] * len(res["masks"]))

    if len(all_masks) == 0:
        # No masks found: return original image (or you can choose to 404)
        overlayed = image.convert("RGBA")
    else:
        masks_tensor = torch.stack(all_masks, dim=0)
        overlayed = overlay_masks_with_labels(image, masks_tensor, all_labels)

    return overlayed


def predict_for_class(image: Image.Image, class_name: str,
                      score_threshold: float = 0.5,
                      mask_threshold: float = 0.5):
    """
    Run SAM3 for a single text prompt and return post-processed results.
    """
    inputs = processor(images=image, text=class_name, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    results = processor.post_process_instance_segmentation(
        outputs,
        threshold=score_threshold,
        mask_threshold=mask_threshold,
        target_sizes=inputs.get("original_sizes").tolist()
    )[0]

    return results


def overlay_masks_with_labels(image: Image.Image,
                              masks: torch.Tensor,
                              labels: Optional[List[str]] = None) -> Image.Image:
    """
    Overlay colored masks and bounding boxes with labels on the image.
    """
    image = image.convert("RGBA")
    masks_np = 255 * masks.cpu().numpy().astype(np.uint8)

    n_masks = masks_np.shape[0]
    if n_masks == 0:
        return image  # nothing to draw

    cmap = matplotlib.colormaps.get_cmap("rainbow").resampled(n_masks)
    colors = [
        tuple(int(c * 255) for c in cmap(i)[:3])
        for i in range(n_masks)
    ]

    # Overlay masks
    for mask, color in zip(masks_np, colors):
        mask_img = Image.fromarray(mask)
        overlay = Image.new("RGBA", image.size, color + (0,))
        alpha = mask_img.point(lambda v: int(v * 0.5))
        overlay.putalpha(alpha)
        image = Image.alpha_composite(image, overlay)

    draw = ImageDraw.Draw(image)

    # Font
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()

    # Draw bounding boxes + labels
    for idx, (mask, color) in enumerate(zip(masks_np, colors)):
        ys, xs = np.where(mask > 0)
        if len(xs) == 0 or len(ys) == 0:
            continue

        x1, y1, x2, y2 = xs.min(), ys.min(), xs.max(), ys.max()
        draw.rectangle([(x1, y1), (x2, y2)], outline=color + (255,), width=3)

        label = labels[idx] if labels and idx < len(labels) else "object"
        text = f"{label}"

        text_bbox = draw.textbbox((0, 0), text, font=font)
        tw = text_bbox[2] - text_bbox[0]
        th = text_bbox[3] - text_bbox[1]

        # text background
        draw.rectangle(
            [(x1, y1 - th - 4), (x1 + tw + 4, y1)],
            fill=(0, 0, 0, 160)
        )
        draw.text((x1 + 2, y1 - th - 2), text, fill=(255, 255, 255), font=font)

    return image


@app.get("/images_list")
def images_list() -> List[str]:
    if not ASSETS_DIR.exists():
        return []
    imgs = []
    for p in ASSETS_DIR.glob("**/*"):
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            imgs.append(str(p))
    return imgs


@app.get("/image")
def get_image(path: str):
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(str(p))


@app.post("/segment_image")
async def segment_image(
    chat_history: str = Form(...),
    classes_json: str = Form(...),
    image: UploadFile = File(...),
):
    try:
        import json
        chat_hist = json.loads(chat_history)
        classes_data = json.loads(classes_json)
        classes = classes_data.get("classes", [])
        if not classes:
            raise ValueError("classes list required")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

    # Save uploaded image to outputs
    img_bytes = await image.read()
    tmp_img_path = OUTPUTS_DIR / f"upload_{image.filename}"
    with open(tmp_img_path, "wb") as f:
        f.write(img_bytes)

    # Run pipeline
    # Persist classes JSON alongside image for pipeline
    classes_path = str(tmp_img_path) + ".classes.json"
    import json
    with open(classes_path, "w", encoding="utf-8") as f:
        json.dump({"classes": classes}, f, ensure_ascii=False, indent=2)

    pipeline = build_pipeline()
    result = pipeline.run(str(tmp_img_path), classes_path, str(OUTPUTS_DIR))

    # Overwrite classes in result with request classes
    result["input"]["classes"] = classes

    # Generate chat answer
    chat_answer = generate_chat_answer(chat_hist, classes)

    return {"chat_answer": chat_answer, "detect_segment": result}
