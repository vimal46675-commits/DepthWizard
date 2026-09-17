import os
import numpy as np
import matplotlib.pyplot as plt

# ============================================
# DEPTHWIZARD
# Calibrated Elevation Visualization
# ============================================

input_path = os.path.join(
    "results",
    "depth_maps",
    "calibrated_elevation.npy"
)

output_dir = os.path.join(
    "results",
    "visualizations"
)

output_path = os.path.join(
    output_dir,
    "calibrated_elevation.png"
)

# --------------------------------------------
# Load calibrated elevation
# --------------------------------------------

print("============================================")
print("CALIBRATED ELEVATION VISUALIZATION")
print("============================================")

if not os.path.exists(input_path):
    raise FileNotFoundError(
        f"Elevation file not found: {input_path}"
    )

elevation = np.load(input_path)

print("Elevation shape:", elevation.shape)
print(f"Minimum elevation: {elevation.min():.2f} m")
print(f"Maximum elevation: {elevation.max():.2f} m")
print(f"Mean elevation: {elevation.mean():.2f} m")

# --------------------------------------------
# Create output directory
# --------------------------------------------

os.makedirs(output_dir, exist_ok=True)

# --------------------------------------------
# Plot elevation map
# --------------------------------------------

plt.figure(figsize=(12, 10))

plt.imshow(elevation)

plt.colorbar(
    label="Elevation (meters)"
)

plt.title(
    "DepthWizard - Calibrated Elevation Map"
)

plt.xlabel("Pixel X")
plt.ylabel("Pixel Y")

plt.tight_layout()

plt.savefig(
    output_path,
    dpi=200
)

plt.close()

print()
print("Elevation visualization saved:")
print(output_path)

print()
print("============================================")
print("VISUALIZATION COMPLETED")
print("============================================")