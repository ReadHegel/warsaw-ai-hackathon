import json
import random
from typing import List, Dict, Any, Union

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from transformers import pipeline, Sam2Model, Sam2Processor
from transformers.image_utils import load_image


# ---------- Utility: random but stable color per class ----------
def color_for_label(label: str):
    random.seed(hash(label) % (2 ** 16))
    return (
        random.randint(80, 255),
        random.randint(80, 255),
        random.randint(80, 255),
    )


# ---------- Main pipeline ----------
class ZeroShotDetSam2Visualizer:
    def __init__(
        self,
        det_checkpoint="google/owlv2-base-patch16-ensemble",
        sam_checkpoint="facebook/sam2.1-hiera-small",
        device="auto"
    ):
        if device == "auto":
            dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            dev = torch.device(device)

        self.device = dev
        det_device_index = dev.index if dev.type == "cuda" else -1

        # Zero-shot detector
        self.detector = pipeline(
            "zero-shot-object-detection",
            model=det_checkpoint,
            device=det_device_index,
        )

        # SAM2
        self.sam_model = Sam2Model.from_pretrained(sam_checkpoint).to(dev)
        self.sam_model.eval()
        self.sam_processor = Sam2Processor.from_pretrained(sam_checkpoint)

    def run(self, image_path: str, classes: List[str], score_threshold=0.35):
        pil_image = load_image(image_path).convert("RGB")
        width, height = pil_image.size

        # --- 1. Zero-shot detection ---
        det_out = self.detector(
            pil_image,
            candidate_labels=classes,
            threshold=score_threshold,
        )

        if not det_out:
            print("No detections found.")
            return pil_image

        # Format boxes for SAM2
        input_boxes = [[
            [
                int(p["box"]["xmin"]),
                int(p["box"]["ymin"]),
                int(p["box"]["xmax"]),
                int(p["box"]["ymax"])
            ]
            for p in det_out
        ]]

        # --- 2. SAM2 segmentation ---
        sam_inputs = self.sam_processor(
            images=pil_image,
            input_boxes=input_boxes,
            return_tensors="pt"
        ).to(self.device)

        with torch.inference_mode():
            sam_outputs = self.sam_model(**sam_inputs, multimask_output=False)

        masks = self.sam_processor.post_process_masks(
            sam_outputs.pred_masks.cpu(),
            sam_inputs["original_sizes"],
        )[0]  # (N, H, W)

        if masks.ndim == 4:
            masks = masks[:, 0]  # enforce (N,H,W)

        masks = masks > 0.5

        # --- 3. Render overlay ---
        overlay = pil_image.copy()
        draw = ImageDraw.Draw(overlay, "RGBA")

        # Optionally load font
        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()

        for pred, mask in zip(det_out, masks):
            label = pred["label"]
            score = float(pred["score"])
            color = color_for_label(label)

            # ---- Draw mask ----
            mask_np = mask.numpy().astype("uint8") * 120  # transparency
            mask_img = Image.fromarray(mask_np, mode="L")
            color_img = Image.new("RGBA", (width, height), color + (120,))
            overlay.paste(color_img, (0, 0), mask_img)

            # ---- Draw box ----
            box = pred["box"]
            xmin, ymin, xmax, ymax = (
                int(box["xmin"]), int(box["ymin"]),
                int(box["xmax"]), int(box["ymax"])
            )
            draw.rectangle([xmin, ymin, xmax, ymax], outline=color, width=3)

            # # ---- Draw label ----
            # caption = f"{label} {score:.2f}"
            # tw, th = draw.textsize(caption, font=font)
            # draw.rectangle([xmin, ymin - th, xmin + tw, ymin], fill=color + (180,))
            # draw.text((xmin, ymin - th), caption, fill=(0, 0, 0), font=font)

        return overlay


# ------------------- Example Usage -------------------
if __name__ == "__main__":
    pipe = ZeroShotDetSam2Visualizer()

    img = pipe.run(
        image_path="input.jpg",
        classes=["person", "dog", "cat"],
        score_threshold=0.4
    )

    img.save("output_overlay.jpg")
    print("Saved → output_overlay.jpg")
