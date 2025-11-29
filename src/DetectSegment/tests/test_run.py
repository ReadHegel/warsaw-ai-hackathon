import os
import random
from pathlib import Path
import urllib.request

from DetectSegment.pipelines.detect_and_segment import DetectAndSegmentPipeline


def download_sample_image(dst_path: str):
    url = "https://images.unsplash.com/photo-1517849845537-4d257902454a?w=1024"  # dog
    Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dst_path)


def download_random_checkpoint(dst_dir: Path) -> str:
    """Download a random SAM checkpoint if none specified.

    Chooses randomly from SAM ViT model weights and downloads into tests/checkpoints/.
    Returns the local path to the downloaded checkpoint.
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    checkpoints = {
        "vit_h": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        "vit_l": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
        "vit_b": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
    }
    # model_type = random.choice(list(checkpoints.keys()))
    model_type = "vit_b"
    url = checkpoints[model_type]
    local_path = dst_dir / f"{model_type}.pth"
    if not local_path.exists():
        print(f"[INFO] Pobieram losowy SAM checkpoint ({model_type}) do {local_path}...")
        urllib.request.urlretrieve(url, str(local_path))
    else:
        print(f"[INFO] Używam istniejącego lokalnego checkpointu: {local_path}")
    return str(local_path)


def main():
    base = Path(__file__).parent
    assets_dir = base / "assets"
    image_path = str(assets_dir / "sample.jpg")
    classes_json_path = str(base / "sample_classes.json")
    output_dir = str(base / "outputs")

    if not os.path.exists(image_path):
        print("Downloading sample image...")
        download_sample_image(image_path)

    # If SAM_CHECKPOINT env is not set, download a random one into tests/checkpoints/
    sam_checkpoint = os.environ.get("SAM_CHECKPOINT")
    checkpoints_dir = base / "checkpoints"
    if not sam_checkpoint:
        print("[WARN] Zmienna SAM_CHECKPOINT nie ustawiona. Pobieram losowy checkpoint...")
        sam_checkpoint = download_random_checkpoint(checkpoints_dir)
    else:
        # If user provided but path doesn't exist, hint.
        if not os.path.exists(sam_checkpoint):
            print(f"[WARN] Podany SAM_CHECKPOINT '{sam_checkpoint}' nie istnieje. Rozważ pobranie lub ustawienie poprawnej ścieżki.")

    # Infer sam_model_type from filename if we downloaded automatically
    inferred_type = "vit_h"
    for t in ["vit_h", "vit_l", "vit_b"]:
        if sam_checkpoint.endswith(f"{t}.pth"):
            inferred_type = t
            break

    pipeline = DetectAndSegmentPipeline(
        detector_model="google/owlvit-base-patch32",
        sam_checkpoint=sam_checkpoint,
        sam_model_type=inferred_type,
        confidence_threshold=0.25,
    )

    result = pipeline.run(image_path, classes_json_path, output_dir)
    print("Pipeline completed. Results saved to:")
    print(output_dir)


if __name__ == "__main__":
    main()
