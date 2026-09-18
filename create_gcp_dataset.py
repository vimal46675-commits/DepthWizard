import csv
import numpy as np

# ============================================================
# DEPTHWIZARD - GCP DATASET CREATION
# ============================================================

DEPTH_PATH = r"results\depth_maps\sentinel_rgb_2048_depth.npy"
OUTPUT_PATH = r"results\gcp_dataset.csv"

# Original Sentinel image pixel coordinates
# Reference elevations obtained from DEM
gcp_points = [
    (4, 166, 10728, 125.44),
    (5, 64, 5195, 107.77),
    (7, 5855, 10900, 148.25),
    (9, 150, 2670, 112.25),
    (10, 166, 8219, 102.05),
    (11, 3233, 10883, 116.71),
]

# Original Sentinel image size
ORIGINAL_SIZE = 10980

# Depth map size
DEPTH_SIZE = 2048

depth = np.load(DEPTH_PATH)

scale = DEPTH_SIZE / ORIGINAL_SIZE

rows = []

print("============================================")
print("GCP DATASET CREATION")
print("============================================")

for gcp_id, original_x, original_y, elevation in gcp_points:

    x = round(original_x * scale)
    y = round(original_y * scale)

    relative_depth = float(depth[y, x])

    rows.append([
        f"GCP{gcp_id}",
        original_x,
        original_y,
        x,
        y,
        relative_depth,
        elevation
    ])

    print(
        f"GCP{gcp_id}: "
        f"Depth Pixel=({x},{y}) | "
        f"Depth={relative_depth:.6f} | "
        f"Elevation={elevation:.2f}m"
    )

with open(OUTPUT_PATH, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "id",
        "original_x",
        "original_y",
        "depth_x",
        "depth_y",
        "relative_depth",
        "reference_elevation"
    ])

    writer.writerows(rows)

print()
print("============================================")
print("DATASET CREATED SUCCESSFULLY")
print("============================================")
print("Output:", OUTPUT_PATH)
print("Valid GCPs:", len(rows))