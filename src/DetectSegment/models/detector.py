from typing import List, Dict, Any, Optional

import torch
from transformers import pipeline


class ZeroShotDetector:
    """
    Zero-shot object detector using OWL-ViT via Hugging Face transformers.
    Accepts a list of candidate classes and returns bounding boxes and scores.
    """

    def __init__(
        self,
        model_name: str = "google/owlvit-base-patch32",
        device: Optional[str] = None,
        confidence_threshold: float = 0.2,
    ) -> None:
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = 0 if device == "cuda" else -1
        self.confidence_threshold = confidence_threshold
        self.detector = pipeline(
            task="zero-shot-object-detection",
            model=model_name,
            device=self.device,
        )

    def predict(self, image: Any, classes: List[str]) -> List[Dict[str, Any]]:
        """
        Args:
            image: PIL.Image, numpy array, or path accepted by transformers pipeline
            classes: list of labels to search for
        Returns:
            List of dicts: {
              'label': str,
              'score': float,
              'box': {'xmin': int, 'ymin': int, 'xmax': int, 'ymax': int}
            }
        """
        outputs = self.detector(image, candidate_labels=classes)
        # Filter by threshold
        results = [o for o in outputs if o.get("score", 0.0) >= self.confidence_threshold]
        return results
