import rasterio
import numpy as np
from PIL import Image
import os
from pathlib import Path

BASE = Path(r"C:\Users\onlys\Downloads\Sentinel28")

def find_band(band):
    matches = list(BASE.rglob(f"*_{band}_10m.jp2"))

    if not matches:
        raise FileNotFoundError(f"{band} file not found")

    print(f"{band}: {matches[0]}")
    return matches[0]


# Find Sentinel-2 bands
b02_path = find_band("B02")
b03_path = find_band("B03")
b04_path = find_band("B04")


# Read bands
with rasterio.open(b02_path) as src:
    blue = src.read(1).astype(np.float32)

with rasterio.open(b03_path) as src:
    green = src.read(1).astype(np.float32)

with rasterio.open(b04_path) as src:
    red = src.read(1).astype(np.float32)


def normalize(arr):
    low = np.percentile(arr, 2)
    high = np.percentile(arr, 98)

    arr = (arr - low) / (high - low)
    arr = np.clip(arr, 0, 1)

    return (arr * 255).astype(np.uint8)


# Convert to 8-bit RGB
red = normalize(red)
green = normalize(green)
blue = normalize(blue)

# Combine RGB
rgb = np.dstack((red, green, blue))

# Create output folder
os.makedirs(r"data\imagery", exist_ok=True)

# Save RGB image
output = r"data\imagery\sentinel_rgb.png"

Image.fromarray(rgb).save(output)

print("--------------------------------")
print("RGB IMAGE CREATED SUCCESSFULLY")
print("--------------------------------")
print(f"Output: {output}")
print(f"Image shape: {rgb.shape}")