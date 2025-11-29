from typing import List, Dict, Any
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from DetectSegment.pipelines.detect_and_segment import DetectAndSegmentPipeline
from DetectSegment.utils.io_utils import load_image

"""FastAPI application for Detect + Segment + Chat reasoning."""

# Optional chat module import
try:
    from UserPromptProcess.chat import (
        generate_classes_with_llm,
        generate_chat_answer,
    )
except Exception:
    # Fallback simple implementations
    def generate_classes_with_llm(chat_history: List[Dict[str, Any]], proposed_classes: List[str], current_image_path: Any) -> List[str]:
        return list(proposed_classes or [])

    def generate_chat_answer(chat_history: List[Dict[str, Any]], classes: List[str], current_image_path: Any, answer: Any) -> str:
        last_user = ""
        for msg in reversed(chat_history or []):
            if msg.get("role") == "user":
                last_user = msg.get("content", "")
                break
        return f"(Fallback) Klasy: {', '.join(classes)}. Ostatnia wiadomość: {last_user}"


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
    """Main endpoint: upload image + chat history + proposed classes.

    Steps:
      1. Parse JSON payloads.
      2. Save uploaded image.
      3. Use vision-language model to refine class list.
      4. Persist refined classes JSON for pipeline.
      5. Run detect+segment pipeline.
      6. Invoke chat answer model for user response.
    """
    try:
        import json
        chat_hist = json.loads(chat_history)
        classes_data = json.loads(classes_json)
        proposed_classes = classes_data.get("classes", [])
        if not proposed_classes:
            raise ValueError("classes list required")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

    # Save uploaded image
    img_bytes = await image.read()
    tmp_img_path = OUTPUTS_DIR / f"upload_{image.filename}"
    with open(tmp_img_path, "wb") as f:
        f.write(img_bytes)

    # Refine classes using LLM with image context
    refined_classes = []
    try:
        refined_classes = generate_classes_with_llm(chat_hist, proposed_classes, str(tmp_img_path))
    except Exception:
        refined_classes = list(proposed_classes)

    # Persist refined classes JSON
    classes_path = str(tmp_img_path) + ".classes.json"
    import json
    with open(classes_path, "w", encoding="utf-8") as f:
        json.dump({"classes": refined_classes}, f, ensure_ascii=False, indent=2)

    # Run pipeline
    pipeline = build_pipeline()
    result = pipeline.run(str(tmp_img_path), classes_path, str(OUTPUTS_DIR))
    result["input"]["classes"] = refined_classes

    # Generate chat answer (LLM-based, fallback handled internally)
    try:
        chat_answer = generate_chat_answer(chat_hist, refined_classes, str(tmp_img_path), result)
    except Exception:
        chat_answer = "Nie udało się wygenerować odpowiedzi chatu."

    return {
        "chat_answer": chat_answer,
        "detect_segment": result,
        "proposed_classes": proposed_classes,
        "refined_classes": refined_classes,
    }
