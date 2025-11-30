import math
from io import BytesIO

import requests
from PIL import Image

BASE_URL = "https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WMS/HighResolution"

# --- your original BBOX in EPSG:2180 ---
minx, miny, maxx, maxy = 509288.45, 611214.95, 509432.12, 611381.00

GRID_COLS = 4
GRID_ROWS = 4
PIXEL_SIZE_M = 0.03  
 
# 1) Split BBOX in map coordinates
dx = maxx - minx
dy = maxy - miny

# column boundaries (x) west → east
col_bounds = [minx + dx * c / GRID_COLS for c in range(GRID_COLS + 1)]
# row boundaries (y) south → north
row_bounds = [miny + dy * r / GRID_ROWS for r in range(GRID_ROWS + 1)]

# 2) Pixel sizes for each col/row (so resolution is ~constant)
col_widths = []
for c in range(GRID_COLS):
    w_m = col_bounds[c + 1] - col_bounds[c]
    col_widths.append(math.ceil(w_m / PIXEL_SIZE_M))

row_heights = []
for r in range(GRID_ROWS):
    h_m = row_bounds[r + 1] - row_bounds[r]
    row_heights.append(math.ceil(h_m / PIXEL_SIZE_M))

mosaic_width = sum(col_widths)
mosaic_height = sum(row_heights)

print("Mosaic size:", mosaic_width, "x", mosaic_height)

mosaic = Image.new("RGB", (mosaic_width, mosaic_height))

headers = {"User-Agent": "Mozilla/5.0 (Python script)"}

for r in range(GRID_ROWS):      # r = 0 is SOUTH, r = GRID_ROWS-1 is NORTH
    for c in range(GRID_COLS):  # c = 0 is WEST,  c = GRID_COLS-1 is EAST
        xmin = col_bounds[c]
        xmax = col_bounds[c + 1]
        ymin = row_bounds[r]
        ymax = row_bounds[r + 1]

        width_px = col_widths[c]
        height_px = row_heights[r]

        bbox_str = f"{xmin},{ymin},{xmax},{ymax}"
        print(f"Tile r={r}, c={c}, BBOX={bbox_str}, size={width_px}x{height_px}")

        params = {
            "SERVICE": "WMS",
            "REQUEST": "GetMap",
            "VERSION": "1.3.0",
            "LAYERS": "Raster",
            "STYLES": "default",
            "FORMAT": "image/png",   # lossless
            "CRS": "EPSG:2180",
            "BBOX": bbox_str,
            "WIDTH": height_px,
            "HEIGHT": width_px,
        }

        resp = requests.get(BASE_URL, params=params, headers=headers, timeout=120)
        resp.raise_for_status()
        # print(resp)
        tile = Image.open(BytesIO(resp.content)).convert("RGB").transpose(method=Image.TRANSVERSE)

        # 3) Paste without any rotation:
        #    image y=0 is TOP, but r=0 is SOUTH → flip rows when pasting
        x_off = sum(col_widths[:c])
        y_off = mosaic_height - sum(row_heights[: r + 1])  # bottom row at bottom
        mosaic.paste(tile, (x_off, y_off))

mosaic.save("geoportal_ortho_4x4_max.png")
print("Saved geoportal_ortho_4x4_max.png")
