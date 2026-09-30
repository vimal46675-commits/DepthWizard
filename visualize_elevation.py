import numpy as np
from PIL import Image

# Load calibrated elevation map
elevation_path = "results/depth_maps/calibrated_elevation.npy"

elevation = np.load(elevation_path)

print("Calibrated elevation map loaded")
print("Shape:", elevation.shape)
print("Minimum elevation:", float(elevation.min()), "m")
print("Maximum elevation:", float(elevation.max()), "m")
print("Mean elevation:", float(elevation.mean()), "m")

# Normalize elevation to 0-255 for visualization
elevation_min = elevation.min()
elevation_max = elevation.max()

normalized = (
    (elevation - elevation_min)
    / (elevation_max - elevation_min)
    * 255
)

normalized = normalized.astype(np.uint8)

# Create grayscale PNG
output_path = "results/visualizations/calibrated_elevation.png"

Image.fromarray(normalized).save(output_path)

print("\nSaved:")
print(output_path)