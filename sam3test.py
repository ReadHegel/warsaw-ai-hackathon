from transformers import Sam3Processor, Sam3Model
import torch
from PIL import Image
import requests
import numpy as np
import matplotlib
from PIL import ImageDraw, ImageFont
import os



def predict_for_class(predictor, img, class_name):
    inputs = processor(images=img, text=class_name, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    results = processor.post_process_instance_segmentation(
        outputs,
        threshold=0.5,
        mask_threshold=0.5,
        target_sizes=inputs.get("original_sizes").tolist()
    )[0]
    return results

device = "cuda" if torch.cuda.is_available() else "cpu"

def overlay_masks_with_labels(image, masks, labels=None):
    image = image.convert("RGBA")
    masks = 255 * masks.cpu().numpy().astype(np.uint8)
    
    n_masks = masks.shape[0]
    cmap = matplotlib.colormaps.get_cmap("rainbow").resampled(n_masks)
    colors = [
        tuple(int(c * 255) for c in cmap(i)[:3])
        for i in range(n_masks)
    ]

    for mask, color in zip(masks, colors):
        mask_img = Image.fromarray(mask)
        overlay = Image.new("RGBA", image.size, color + (0,))
        alpha = mask_img.point(lambda v: int(v * 0.5))
        overlay.putalpha(alpha)
        image = Image.alpha_composite(image, overlay)

    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    for idx, (mask, color) in enumerate(zip(masks, colors)):
        ys, xs = np.where(mask > 0)
        if len(xs) == 0 or len(ys) == 0:
            continue

        x1, y1, x2, y2 = xs.min(), ys.min(), xs.max(), ys.max()
        draw.rectangle([(x1, y1), (x2, y2)], outline=color + (255,), width=3)

        label = labels[idx] if labels else "object"
        text = f"{label}"

        text_size = draw.textbbox((0, 0), text, font=font)
        tw, th = text_size[2] - text_size[0], text_size[3] - text_size[1]

        draw.rectangle([(x1, y1 - th - 4), (x1 + tw + 4, y1)], fill=(0, 0, 0, 160))
        draw.text((x1 + 2, y1 - th - 2), text, fill=(255, 255, 255), font=font)

    return image

model = Sam3Model.from_pretrained("facebook/sam3").to(device)
processor = Sam3Processor.from_pretrained("facebook/sam3")

text_prompts = ['truck', 'car','dirt roads junction', 'tree cluster']

# Load image
# image_url = "http://images.cocodataset.org/val2017/000000077595.jpg"
# image = Image.open(requests.get(image_url, stream=True).raw).convert("RGB")
for img_path in os.listdir('test_image'):
    image = Image.open(os.path.join('test_image', img_path)).convert("RGB")
# Segment using text prompt
# inputs = processor(images=image, text=text_prompts, return_tensors="pt").to(device)

# with torch.no_grad():
#     outputs = model(**inputs)

# # Post-process results
# results = processor.post_process_instance_segmentation(
#     outputs,
#     threshold=0.7,
#     mask_threshold=0.5,
#     target_sizes=inputs.get("original_sizes").tolist()
# )[0]

# print(f"Found {len(results['masks'])} objects")
    masks = []
    labels = []
    for class_name in text_prompts:
        res = predict_for_class(model, image, class_name)
        if len(res['masks']) == 0:
            continue
        masks.extend(res['masks'])
        labels.extend([class_name] * len(res['masks']))

    if len(masks) == 0:
        print("No objects found")
        continue
    masks = torch.stack(masks, dim=0)

    overlayed_image = overlay_masks_with_labels(image, masks, labels)
    overlayed_image.save(f"sam3_output_{img_path}.png")

# def overlay_masks(image, masks):
#     image = image.convert("RGBA")
#     masks = 255 * masks.cpu().numpy().astype(np.uint8)
    
#     n_masks = masks.shape[0]
#     cmap = matplotlib.colormaps.get_cmap("rainbow").resampled(n_masks)
#     colors = [
#         tuple(int(c * 255) for c in cmap(i)[:3])
#         for i in range(n_masks)
#     ]

#     for mask, color in zip(masks, colors):
#         mask = Image.fromarray(mask)
#         overlay = Image.new("RGBA", image.size, color + (0,))
#         alpha = mask.point(lambda v: int(v * 0.5))
#         overlay.putalpha(alpha)
#         image = Image.alpha_composite(image, overlay)
#     return image

# overlay_masks(image, results["masks"]).save("sam3_output.png")
# Results contain:
# - masks: Binary masks resized to original image size
# - boxes: Bounding boxes in absolute pixel coordinates (xyxy format)
# - scores: Confidence scores
