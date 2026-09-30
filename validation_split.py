import csv
import numpy as np

# ============================================================
# DEPTHWIZARD - CALIBRATION + VALIDATION
# ============================================================

CSV_PATH = r"results\gcp_dataset.csv"

# ------------------------------------------------------------
# Load GCP dataset
# ------------------------------------------------------------

depth_values = []
elevation_values = []
gcp_ids = []

with open(CSV_PATH, "r") as file:

    reader = csv.DictReader(file)

    for row in reader:
        gcp_ids.append(row["id"])
        depth_values.append(float(row["relative_depth"]))
        elevation_values.append(float(row["reference_elevation"]))

D = np.array(depth_values)
Z = np.array(elevation_values)

print("============================================")
print("CALIBRATION + VALIDATION")
print("============================================")

print("Total valid GCPs:", len(D))
print()

# ------------------------------------------------------------
# 4 GCPs for calibration
# 2 GCPs for validation
# ------------------------------------------------------------

calibration_indices = [0, 1, 2, 3]
validation_indices = [4, 5]

D_cal = D[calibration_indices]
Z_cal = Z[calibration_indices]

D_val = D[validation_indices]
Z_val = Z[validation_indices]

print("Calibration GCPs:")
for i in calibration_indices:
    print(
        f"{gcp_ids[i]} | "
        f"Depth={D[i]:.6f} | "
        f"Reference={Z[i]:.2f}m"
    )

print()

print("Validation GCPs:")
for i in validation_indices:
    print(
        f"{gcp_ids[i]} | "
        f"Depth={D[i]:.6f} | "
        f"Reference={Z[i]:.2f}m"
    )

# ------------------------------------------------------------
# Linear calibration
# Z = aD + b
# ------------------------------------------------------------

a, b = np.polyfit(D_cal, Z_cal, 1)

print()
print("============================================")
print("LINEAR CALIBRATION")
print("============================================")

print(f"Scale  : {a:.6f}")
print(f"Offset : {b:.6f}")

# ------------------------------------------------------------
# Training performance
# ------------------------------------------------------------

Z_cal_pred = a * D_cal + b

train_errors = Z_cal_pred - Z_cal

train_mae = np.mean(np.abs(train_errors))
train_rmse = np.sqrt(np.mean(train_errors ** 2))

print()
print("Training MAE :", f"{train_mae:.3f} m")
print("Training RMSE:", f"{train_rmse:.3f} m")

# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

Z_val_pred = a * D_val + b

val_errors = Z_val_pred - Z_val

val_mae = np.mean(np.abs(val_errors))
val_rmse = np.sqrt(np.mean(val_errors ** 2))

# R²
ss_res = np.sum((Z_val - Z_val_pred) ** 2)
ss_tot = np.sum((Z_val - np.mean(Z_val)) ** 2)

if ss_tot == 0:
    r2 = float("nan")
else:
    r2 = 1 - (ss_res / ss_tot)

print()
print("============================================")
print("INDEPENDENT VALIDATION")
print("============================================")

for i, predicted, reference, error in zip(
    validation_indices,
    Z_val_pred,
    Z_val,
    val_errors
):

    print(
        f"{gcp_ids[i]}: "
        f"Reference={reference:.2f}m | "
        f"Predicted={predicted:.2f}m | "
        f"Error={error:+.2f}m"
    )

print()
print("============================================")
print("FINAL VALIDATION METRICS")
print("============================================")

print("Validation MAE :", f"{val_mae:.3f} m")
print("Validation RMSE:", f"{val_rmse:.3f} m")
print("Validation R²  :", f"{r2:.4f}")

print()
print("============================================")
print("EQUATION")
print("============================================")

print(
    f"Elevation = {a:.6f} * RelativeDepth + ({b:.6f})"
)

print()
print("NOTE:")
print("Only 2 validation GCPs are currently available.")
print("This is a preliminary validation result.")