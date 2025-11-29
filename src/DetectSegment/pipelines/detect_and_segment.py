from typing import Dict, Any, List
from pathlib import Path

from PIL import Image

from ..models.detector import ZeroShotDetector
from ..models.sam_segmenter import SAMSegmenter
from ..utils.io_utils import load_json, save_json, load_image, save_image
from ..utils.viz_utils import draw_boxes, overlay_mask
from ..utils.device_utils import get_default_device


class DetectAndSegmentPipeline:
    """
    Pipeline that:
    - Loads classes from JSON
    - Runs zero-shot object detection (OWL-ViT)
    - Uses boxes to prompt SAM to generate masks
    - Saves visualizations and returns structured results
    """

    def __init__(
        self,
        detector_model: str = "google/owlvit-base-patch32",
        sam_checkpoint: str = "sam_vit_h.pth",
        sam_model_type: str = "vit_h",
        confidence_threshold: float = 0.25,
        device: str = None,
    ) -> None:
        device = device or get_default_device()
        self.detector = ZeroShotDetector(
            model_name=detector_model,
            device=device,
            confidence_threshold=confidence_threshold,
        )
        self.segmenter = SAMSegmenter(
            sam_checkpoint=sam_checkpoint,
            model_type=sam_model_type,
            device=device,
        )

    def run(
        self,
        image_path: str,
        classes_json_path: str,
        output_dir: str,
    ) -> Dict[str, Any]:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        classes_data = load_json(classes_json_path)
        classes = classes_data.get("classes", [])
        if not isinstance(classes, list) or len(classes) == 0:
            raise ValueError("JSON must include a non-empty 'classes' list.")

        image = load_image(image_path)

        detections: List[Dict[str, Any]] = self.detector.predict(image, classes)

        # Save boxes visualization
        boxes_vis = draw_boxes(image, detections)
        boxes_vis_path = str(Path(output_dir) / "boxes_visualized.png")
        save_image(boxes_vis_path, boxes_vis)

        # Segment with SAM using boxes
        seg_results = self.segmenter.segment_with_boxes(image, detections)

        # Save mask overlays per detection
        mask_paths = []
        for idx, seg in enumerate(seg_results):
            mask_img = overlay_mask(image, seg["mask"])  # default green overlay
            mask_path = str(Path(output_dir) / f"mask_overlay_{idx}.png")
            save_image(mask_path, mask_img)
            mask_paths.append(mask_path)

        # Package results JSON
        result = {
            "input": {
                "image_path": image_path,
                "classes_json_path": classes_json_path,
                "classes": classes,
            },
            "detections": detections,
            "boxes_visualization": boxes_vis_path,
            "segmentations": [
                {
                    "label": seg.get("label"),
                    "score": seg.get("score"),
                    "box": seg.get("box"),
                    "mask_shape": list(seg["mask"].shape),
                    "mask_overlay_path": mask_paths[i],
                }
                for i, seg in enumerate(seg_results)
            ],
        }
        out_json = str(Path(output_dir) / "results.json")
        save_json(out_json, result)
        return result
