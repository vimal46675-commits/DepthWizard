import os
import numpy as np

# ============================================
# DEPTHWIZARD
# FINAL GCP CALIBRATION EVALUATION
# ============================================

depth_path = os.path.join(
    "results",
    "depth_maps",
    "sentinel_rgb_2048_depth.npy"
)

# Calibration parameters obtained earlier
SCALE = -2.725220
OFFSET = 110.186834

# GCP data:
# X, Y, Reference Elevation (meters)
GCPs = [
    (159, 687, 108.82),
    (29, 1588, 105.83),
    (314, 2004, 107.69),
    (1250, 1998, 99.41),
    (857, 559, 106.82),
    (1549, 817, 99.52),
]


# ============================================
# LOAD DEPTH MAP
# ============================================

print("============================================")
print("DEPTHWIZARD FINAL CALIBRATION EVALUATION")
print("============================================")

if not os.path.exists(depth_path):
    raise FileNotFoundError(
        f"Depth map not found: {depth_path}"
    )

depth = np.load(depth_path)

print("Depth map shape:", depth.shape)
print()


# ============================================
# CALCULATE PREDICTIONS
# ============================================

reference = []
predicted = []
errors = []

print("GCP EVALUATION")
print("--------------------------------------------")

for i, (x, y, ref_elevation) in enumerate(GCPs, start=1):

    relative_depth = float(depth[y, x])

    predicted_elevation = (
        SCALE * relative_depth + OFFSET
    )

    error = predicted_elevation - ref_elevation

    reference.append(ref_elevation)
    predicted.append(predicted_elevation)
    errors.append(error)

    print(
        f"GCP {i}: "
        f"Reference={ref_elevation:.2f}m | "
        f"Predicted={predicted_elevation:.2f}m | "
        f"Error={error:+.2f}m"
    )


# ============================================
# CONVERT TO NUMPY
# ============================================

reference = np.array(reference)
predicted = np.array(predicted)
errors = np.array(errors)


# ============================================
# EVALUATION METRICS
# ============================================

absolute_errors = np.abs(errors)

rmse = float(
    np.sqrt(np.mean(errors ** 2))
)

mae = float(
    np.mean(absolute_errors)
)

max_error = float(
    np.max(absolute_errors)
)

# R² calculation
ss_res = np.sum(
    (reference - predicted) ** 2
)

ss_tot = np.sum(
    (reference - np.mean(reference)) ** 2
)

if ss_tot == 0:
    r2 = float("nan")
else:
    r2 = float(1 - (ss_res / ss_tot))


# ============================================
# FINAL REPORT
# ============================================

print()
print("============================================")
print("FINAL EVALUATION REPORT")
print("============================================")

print(f"Number of GCPs       : {len(GCPs)}")
print(f"RMSE                 : {rmse:.3f} m")
print(f"MAE                  : {mae:.3f} m")
print(f"Maximum Error        : {max_error:.3f} m")
print(f"R²                   : {r2:.4f}")

print()
print("Calibration Equation:")
print(
    f"Elevation = {SCALE:.6f} * RelativeDepth "
    f"+ ({OFFSET:.6f})"
)

print()
print("============================================")
print("EVALUATION COMPLETED")
print("============================================")