from typing import List, Dict, Any, Tuple

import torch
import numpy as np
from PIL import Image

try:
    # SAM v1
    from segment_anything import sam_model_registry, SamPredictor
except Exception:
    sam_model_registry = None
    SamPredictor = None


class SAMSegmenter:
    """
    Segment Anything (SAM) segmenter.
    Uses detected boxes (x1,y1,x2,y2) as prompts to generate masks.
    """

    def __init__(
        self,
        sam_checkpoint: str,
        model_type: str = "vit_h",
        device: str = None,
    ) -> None:
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        if sam_model_registry is None:
            raise RuntimeError(
                "segment_anything is not installed. Please install the SAM package."
            )
        self.device = device
        self.sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
        self.sam.to(device)
        self.predictor = SamPredictor(self.sam)

    @staticmethod
    def _box_to_np(box: Dict[str, int]) -> np.ndarray:
        return np.array([box["xmin"], box["ymin"], box["xmax"], box["ymax"]])

    def segment_with_boxes(
        self, image: Image.Image, boxes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Args:
            image: PIL Image
            boxes: list of detection entries with 'box'
        Returns:
            List of dicts with {'mask': np.ndarray(H,W), 'box': box, 'label': str, 'score': float}
        """
        image_np = np.array(image)
        self.predictor.set_image(image_np)
        results = []
        for det in boxes:
            b = det["box"]
            input_box = self._box_to_np(b)
            masks, scores, _ = self.predictor.predict(
                box=input_box,
                multimask_output=False,
            )
            # masks: list of (H, W) boolean arrays
            if len(masks) > 0:
                results.append(
                    {
                        "mask": masks[0],
                        "box": b,
                        "label": det.get("label"),
                        "score": det.get("score"),
                    }
                )
        return results
