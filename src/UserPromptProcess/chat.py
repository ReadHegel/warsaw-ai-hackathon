from typing import List, Dict, Any, Tuple
from pathlib import Path

import json

from PIL import Image


def _extract_last_user_message(chat_history: List[Dict[str, Any]]) -> str:
    last_user = ""
    for msg in reversed(chat_history or []):
        if msg.get("role") == "user":
            last_user = msg.get("content", "")
            break
    return last_user


def _load_image(image_path: Any) -> Image.Image:
    p = Path(str(image_path))
    return Image.open(p).convert("RGB")


def _vision_llm_suggest_classes(
    image: Image.Image, chat_context: str
) -> Tuple[List[str], str]:
    """Try a vision-capable LLM (e.g., LLaVA) to suggest site classes.

    Returns (classes, justification). Falls back to a heuristic if model is unavailable.
    """
    try:
        # LLaVA v1.5 via transformers (requires large VRAM; A100 is suitable)
        from transformers import AutoProcessor, AutoModelForCausalLM

        model_id = "liuhaotian/llava-v1.5-7b-hf"
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype="auto",
            device_map="auto",
        )

        system_prompt = (
            "You are an expert vision-language assistant analyzing a construction site image. "
            "List 6-10 likely object classes present or relevant on a construction site, "
            "considering the visible content. Prefer concise, single-word or short labels. "
            "Output only a comma-separated list."
        )
        user_prompt = f"Context: {chat_context}\nImage analysis:"

        inputs = processor(images=image, text=[system_prompt, user_prompt], return_tensors="pt").to(model.device)
        generate_ids = model.generate(**inputs, max_new_tokens=128)
        generated = processor.batch_decode(generate_ids, skip_special_tokens=True)[0]

        # Extract last comma-separated segment
        text = generated.split("\n")[-1]
        raw_classes = [c.strip() for c in text.split(",") if c.strip()]

        # Basic normalization
        canonical = {
            "helmet": "helmet",
            "hard hat": "helmet",
            "vest": "safety vest",
            "safety vest": "safety vest",
            "gloves": "gloves",
            "boots": "boots",
            "excavator": "excavator",
            "crane": "crane",
            "bulldozer": "bulldozer",
            "dump truck": "dump truck",
            "loader": "loader",
            "wheel loader": "loader",
            "steel beam": "steel beam",
            "rebar": "rebar",
            "concrete mixer": "concrete mixer",
            "barrier": "barrier",
            "traffic cone": "traffic cone",
            "cone": "traffic cone",
            "scaffolding": "scaffolding",
            "ladder": "ladder",
            "generator": "generator",
            "cable": "cable",
            "pipe": "pipe",
            "container": "container",
            "dumpster": "dumpster",
            "sign": "sign",
            "person": "person",
        }
        classes = []
        for c in raw_classes:
            key = c.lower()
            classes.append(canonical.get(key, key))

        justification = (
            "Wybrane klasy pochodzą z analizy obrazu przez LLaVA "
            "z uwzględnieniem kontekstu rozmowy. Zwracamy typowe obiekty "
            "placu budowy i elementy BHP oraz ciężkie maszyny."
        )
        return classes, justification
    except Exception:
        # Heuristic fallback using keywords and common construction site items
        baseline = [
            "helmet",
            "safety vest",
            "gloves",
            "boots",
            "crane",
            "excavator",
            "bulldozer",
            "dump truck",
            "traffic cone",
            "scaffolding",
            "ladder",
            "rebar",
            "concrete mixer",
            "barrier",
            "generator",
            "pipe",
            "container",
            "person",
        ]
        justification = (
            "Model LLaVA nie był dostępny, użyto heurystyk: typowe obiekty "
            "placu budowy oraz elementy BHP zostały dobrane jako klasy bazowe."
        )
        return baseline, justification


def generate_classes_with_llm(
    chat_history: List[Dict[str, Any]], proposed_classes: List[str], current_image_path: Any
) -> List[str]:
    """Generate classes relevant to a construction site using a vision LLM.

    - Considers `chat_history` context and the current image.
    - Produces several candidate classes and appends `proposed_classes`.
    - Returns a deduplicated, concise list.
    """
    chat_context = _extract_last_user_message(chat_history)
    image = _load_image(current_image_path)
    llm_classes, _ = _vision_llm_suggest_classes(image, chat_context)

    combined = list(llm_classes) + list(proposed_classes or [])

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for c in combined:
        key = str(c).strip().lower()
        if key and key not in seen:
            seen.add(key)
            deduped.append(key)
    return deduped


def generate_chat_answer(
    chat_history: List[Dict[str, Any]], classes: List[str], current_image_path: Any, answer: Any
) -> str:
    """Użyj modelu wizja+język (np. LLaVA) aby odpowiedzieć użytkownikowi na
    jego ostatnie pytanie, bazując na:
      - obrazie źródłowym (`current_image_path`)
      - obrazie z wizualizacją detekcji (boxes_visualization)
      - pierwszym obrazie maski (mask_overlay_0.png jeśli istnieje)
      - JSON wyników segmentacji (`answer`)

    Jeśli model nie jest dostępny: zwróć klasyczny fallback tekstowy podsumowujący.
    """
    last_user_question = _extract_last_user_message(chat_history)

    # Ładuj JSON wyników
    try:
        result = answer if isinstance(answer, dict) else json.loads(answer)
    except Exception:
        result = {}

    detections = result.get("detections", [])
    segments = result.get("segmentations", [])
    boxes_vis_path = result.get("boxes_visualization")
    # Spróbuj znaleźć pierwszą maskę
    first_mask_path = None
    for seg in segments:
        p = seg.get("mask_overlay_path")
        if p:
            first_mask_path = p
            break

    # Przygotuj zwięzły kontekst JSON dla promptu
    def _shorten_detections(dets: List[Dict[str, Any]]) -> str:
        parts = []
        for d in dets[:12]:  # ogranicz liczbę wpisów
            lbl = d.get("label")
            score = d.get("score")
            box = d.get("box")
            parts.append(f"{lbl} (score={score:.2f}, box={box})")
        return "; ".join(parts) if parts else "(brak detekcji)"

    detections_summary = _shorten_detections(detections)
    classes_str = ", ".join(classes or [])

    system_prompt = (
        "Jesteś ekspertem analizy obrazu dla placu budowy. Masz dane z detekcji i "
        "segmentacji oraz pytanie użytkownika. Odpowiedz po polsku, zwięźle, uwzględniając co wykryto, "
        "które klasy zostały użyte oraz jeśli to możliwe, opisz kontekst bezpieczeństwa. Nie spekuluj "
        "nad obiektami nieobecnymi."
    )
    user_prompt = (
        f"Pytanie użytkownika: '{last_user_question}'\n"
        f"Użyte klasy: {classes_str}\n"
        f"Detekcje: {detections_summary}\n"
        f"Segmentacje: {len(segments)} masek\n"
        "Odpowiedz bazując na obrazach i danych."
    )

    # Spróbuj modeli LLaVA
    try:
        from transformers import AutoProcessor, AutoModelForCausalLM
        import torch

        model_id = "liuhaotian/llava-v1.5-7b-hf"
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype="auto", device_map="auto"
        )

        # Załaduj obrazy kontekstowe (lista)
        images = []
        try:
            images.append(_load_image(current_image_path))
        except Exception:
            pass
        for extra_path in [boxes_vis_path, first_mask_path]:
            if extra_path:
                try:
                    images.append(_load_image(extra_path))
                except Exception:
                    pass

        # Jeśli brak obrazów, fallback do tekstowego
        if not images:
            raise RuntimeError("Brak obrazów do analizy LLaVA")

        inputs = processor(images=images, text=[system_prompt, user_prompt], return_tensors="pt").to(model.device)
        generate_ids = model.generate(**inputs, max_new_tokens=256)
        raw_output = processor.batch_decode(generate_ids, skip_special_tokens=True)[0]
        # Weź ostatni fragment jako odpowiedź
        llm_answer = raw_output.split("\n")[-1].strip()
        if not llm_answer:
            llm_answer = raw_output.strip()
        return llm_answer
    except Exception:
        # Fallback tekstowy
        found_labels = [str(d.get("label", "")).strip() for d in detections if d.get("label")]
        found_str = ", ".join(found_labels) if found_labels else "brak pewnych wykryć"
        justification = result.get("justification") or (
            "Model LLaVA niedostępny – odpowiedź oparta na danych z detektora i segmentacji."
        )
        return (
            f"Odpowiedź (fallback): W obrazie wykryto: {found_str}. Użyte klasy: {classes_str}. "
            f"Segmentacji: {len(segments)}. {justification} Pytanie użytkownika: '{last_user_question}'."
        )
