import json
import random
from typing import List, Dict, Any, Union

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from transformers import (
    AutoProcessor,
    AutoModelForZeroShotObjectDetection,
    Sam2Model,
    Sam2Processor,
    infer_device,
)
from transformers.image_utils import load_image


# ---------------- Utility: stable label colors ----------------
def color_for_label(label: str):
    random.seed(hash(label) % (2**16))
    return (
        random.randint(60, 255),
        random.randint(60, 255),
        random.randint(60, 255),
    )


# -------------------- Main Pipeline ---------------------------
class GroundingDinoSam2Visualizer:
    def __init__(
        self,
        det_checkpoint="IDEA-Research/grounding-dino-2.0-large",
        sam_checkpoint="facebook/sam2.1-hiera-small-image",
        device="auto"
    ):
        # resolve device
        device = infer_device() if device == "auto" else torch.device(device)
        self.device = device

        # -------- Grounding DINO --------
        self.dino_processor = AutoProcessor.from_pretrained(det_checkpoint)
        self.dino_model = AutoModelForZeroShotObjectDetection.from_pretrained(
            det_checkpoint
        ).to(device)
        self.dino_model.eval()

        # -------- SAM2 --------
        self.sam_processor = Sam2Processor.from_pretrained(sam_checkpoint)
        self.sam_model = Sam2Model.from_pretrained(sam_checkpoint).to(device)
        self.sam_model.eval()

    # -----------------------------------------------------------
    def run(self, image_path: str, classes: List[str], box_threshold=0.3, text_threshold=0.25):
        """
        classes: list of target labels e.g. ["person", "dog"]
        """
        pil_image = load_image(image_path).convert("RGB")
        width, height = pil_image.size

        # Prepare text prompt: comma-separated
        # text_prompt = ", ".join(classes)
        text_prompt = ""
        for cl in classes:
            text_prompt += cl
            text_prompt += ". "

        text_prompt = text_prompt[:-1]
        print(text_prompt)


        # --------- 1) Grounding DINO inference ---------
        inputs = self.dino_processor(
            images=pil_image,
            text=text_prompt,
            return_tensors="pt"
        ).to(self.device)

        with torch.inference_mode():
            outputs = self.dino_model(**inputs)

        # Post-process to get boxes
        results = self.dino_processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            threshold=box_threshold,
            text_threshold=text_threshold,
            target_sizes=[pil_image.size[::-1]],  # (height, width)
        )[0]

        print(results)
        boxes = results["boxes"]       # shape: (N,4) [xmin,ymin,xmax,ymax]
        scores = results["scores"]     # shape: (N)
        labels = results["labels"]     # shape: (N) textual labels

        if len(boxes) == 0:
            print("No detections found.")
            return pil_image

        # Format boxes for SAM2 expected format: [1, N, 4]
        sam_boxes = [[
            [int(x) for x in box.tolist()]
            for box in boxes
        ]]

        # --------- 2) SAM2 segmentation from boxes ---------
        sam_inputs = self.sam_processor(
            images=pil_image,
            input_boxes=sam_boxes,
            return_tensors="pt"
        ).to(self.device)

        with torch.inference_mode():
            sam_outputs = self.sam_model(**sam_inputs, multimask_output=False)

        masks = self.sam_processor.post_process_masks(
            sam_outputs.pred_masks.cpu(),
            sam_inputs["original_sizes"],
        )[0]  # now (N, H, W)

        if masks.ndim == 4:
            masks = masks[:, 0]  # enforce (N, H, W)

        masks = masks > 0.9

        # --------- 3) Render overlay output ---------
        overlay = pil_image.copy()
        drawer = ImageDraw.Draw(overlay, "RGBA")

        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()

        for box, score, label, mask in zip(boxes, scores, labels, masks):
            color = color_for_label(label)

            # ---- mask ----
            mask_np = mask.numpy().astype("uint8") * 140
            mask_img = Image.fromarray(mask_np, mode="L")
            tint = Image.new("RGBA", (width, height), color + (140,))
            overlay.paste(tint, (0, 0), mask_img)

            # ---- bounding box ----
            xmin, ymin, xmax, ymax = map(int, box.tolist())
            drawer.rectangle([xmin, ymin, xmax, ymax], outline=color, width=3)

            # ---- label text ----
            # caption = f"{label} {float(score):.2f}"
            # tw, th = drawer.textsize(caption, font=font)
            # drawer.rectangle([xmin, ymin - th, xmin + tw, ymin], fill=color + (210,))
            # drawer.text((xmin, ymin - th), caption, fill=(0, 0, 0), font=font)

        return overlay


# ------------------- Example Usage -------------------
if __name__ == "__main__":
    pipe = GroundingDinoSam2Visualizer(
        det_checkpoint="IDEA-Research/grounding-dino-base",
        sam_checkpoint="facebook/sam2.1-hiera-large",
        device="cuda"
    )

    out = pipe.run(
        "../../test_image/geoportal_ortho_5cm.jpg",
        classes=[
            "building",
            "road",
            "tree",
            "car",
            "waterbody",
            "sidewalk",
            "bicycle lane",
            "parking lot",
        ],
        # classes=["person", "dog", "cat", "car", "bicycle"],
        box_threshold=0.3,
        text_threshold=0.15
    )

    out.save("output_overlay1.jpg")
    print("Saved → output_overlay1.jpg")