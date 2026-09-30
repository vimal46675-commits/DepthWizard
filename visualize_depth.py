import numpy as np
import cv2

# Input raw depth
depth = np.load("output/test_depth.npy")

print("Depth loaded successfully")
print("Shape:", depth.shape)
print("Min:", depth.min())
print("Max:", depth.max())
print("Mean:", depth.mean())

# Normalize depth to 0-255
depth_normalized = cv2.normalize(
    depth,
    None,
    0,
    255,
    cv2.NORM_MINMAX
)

depth_normalized = depth_normalized.astype(np.uint8)

# Save visualization
cv2.imwrite(
    "output/depth_visualization.png",
    depth_normalized
)

print("Visualization saved to:")
print("output/depth_visualization.png")