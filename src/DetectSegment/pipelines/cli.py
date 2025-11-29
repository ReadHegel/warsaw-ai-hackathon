import argparse
from DetectSegment.pipelines.detect_and_segment import DetectAndSegmentPipeline


def build_parser():
    p = argparse.ArgumentParser("DetectSegment CLI")
    p.add_argument("image", help="Path to input image")
    p.add_argument("classes_json", help="Path to JSON with 'classes' list")
    p.add_argument("output_dir", help="Directory to write results")
    p.add_argument("--detector_model", default="google/owlvit-base-patch32")
    p.add_argument("--sam_checkpoint", required=True, help="Path to SAM checkpoint .pth")
    p.add_argument("--sam_model_type", default="vit_h", choices=["vit_h", "vit_l", "vit_b"])
    p.add_argument("--confidence_threshold", type=float, default=0.25)
    return p


def main():
    args = build_parser().parse_args()
    pipeline = DetectAndSegmentPipeline(
        detector_model=args.detector_model,
        sam_checkpoint=args.sam_checkpoint,
        sam_model_type=args.sam_model_type,
        confidence_threshold=args.confidence_threshold,
    )
    result = pipeline.run(args.image, args.classes_json, args.output_dir)
    print("Results JSON:")
    print(result["input"])  # brief confirmation
    print("Detections:")
    print(len(result["detections"]))


if __name__ == "__main__":
    main()
