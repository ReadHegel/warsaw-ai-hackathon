DetectSegment: Zero-shot Detection + SAM Segmentation

Overview
- Zero-shot object detection via OWL-ViT (Hugging Face transformers pipeline).
- Box prompts feed into SAM (Segment Anything) to produce masks.
- Designed for local GPU execution and easy model swapping.

Structure
- pipelines/: Orchestrates detection + segmentation and result packaging.
- models/: Model loaders (detector and SAM variants).
- utils/: I/O, JSON parsing, visualization, and device utilities.
- tests/: Sample JSON, test scripts, and assets folder.

Quick Start
1) Create a venv and install deps (see usage in repo root instructions below from pipeline CLI).
2) Run the test script to download an image and execute the full pipeline.

Notes
- If SAM2 is unavailable in your environment, the integration uses SAM v1 by default.
- You can swap the detector model (e.g., different OWL-ViT checkpoints) and SAM variants by editing `models/*.py`.
