import numpy as np
import pandas as pd

print("============================================")
print("DEPTHWIZARD CALIBRATION METHOD COMPARISON")
print("============================================")

# -------------------------------------------------
# LOAD GCP DATASET
# -------------------------------------------------

CSV_PATH = r"results\gcp_dataset.csv"

df = pd.read_csv(CSV_PATH)

print(f"Total GCPs: {len(df)}")
print()

print("Dataset columns:", list(df.columns))
print()


# -------------------------------------------------
# CHECK REQUIRED COLUMNS
# -------------------------------------------------

required_columns = [
    "id",
    "relative_depth",
    "reference_elevation"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Required column missing: {column}"
        )


# -------------------------------------------------
# CALIBRATION / VALIDATION SPLIT
#
# SAME SPLIT USED PREVIOUSLY:
# First 6 GCPs = Calibration
# Last 3 GCPs = Validation
# -------------------------------------------------

cal = df.iloc[:6].copy()
val = df.iloc[6:].copy()

D_cal = cal["relative_depth"].to_numpy(dtype=float)
Z_cal = cal["reference_elevation"].to_numpy(dtype=float)

D_val = val["relative_depth"].to_numpy(dtype=float)
Z_val = val["reference_elevation"].to_numpy(dtype=float)


# -------------------------------------------------
# METRICS FUNCTION
# -------------------------------------------------

def calculate_metrics(reference, predicted):

    error = predicted - reference

    mae = np.mean(np.abs(error))

    rmse = np.sqrt(
        np.mean(error ** 2)
    )

    ss_res = np.sum(
        (reference - predicted) ** 2
    )

    ss_tot = np.sum(
        (reference - np.mean(reference)) ** 2
    )

    if ss_tot == 0:
        r2 = np.nan
    else:
        r2 = 1 - (ss_res / ss_tot)

    return mae, rmse, r2


# =================================================
# 1. LINEAR REGRESSION
#
# Elevation = Scale * Depth + Offset
# =================================================

linear_coefficients = np.polyfit(
    D_cal,
    Z_cal,
    1
)

linear_scale = linear_coefficients[0]
linear_offset = linear_coefficients[1]

linear_cal_pred = (
    linear_scale * D_cal
    + linear_offset
)

linear_val_pred = (
    linear_scale * D_val
    + linear_offset
)

linear_train_mae, linear_train_rmse, _ = calculate_metrics(
    Z_cal,
    linear_cal_pred
)

linear_mae, linear_rmse, linear_r2 = calculate_metrics(
    Z_val,
    linear_val_pred
)


# =================================================
# 2. POLYNOMIAL REGRESSION
#
# Degree 2:
# Elevation = aD² + bD + c
# =================================================

poly_coefficients = np.polyfit(
    D_cal,
    Z_cal,
    2
)

poly_cal_pred = np.polyval(
    poly_coefficients,
    D_cal
)

poly_val_pred = np.polyval(
    poly_coefficients,
    D_val
)

poly_train_mae, poly_train_rmse, _ = calculate_metrics(
    Z_cal,
    poly_cal_pred
)

poly_mae, poly_rmse, poly_r2 = calculate_metrics(
    Z_val,
    poly_val_pred
)


# =================================================
# 3. ROBUST LINEAR REGRESSION
#
# Iteratively reduces the influence of large
# residuals/outliers.
# =================================================

def robust_linear_fit(x, y, iterations=30):

    X = np.column_stack([
        x,
        np.ones(len(x))
    ])

    weights = np.ones(len(x))

    for _ in range(iterations):

        W = np.diag(weights)

        beta = np.linalg.pinv(
            X.T @ W @ X
        ) @ (
            X.T @ W @ y
        )

        prediction = X @ beta

        residual = y - prediction

        median_residual = np.median(residual)

        mad = np.median(
            np.abs(
                residual - median_residual
            )
        )

        if mad < 1e-8:
            break

        threshold = 1.345 * mad

        abs_residual = np.abs(residual)

        weights = np.where(
            abs_residual <= threshold,
            1.0,
            threshold / abs_residual
        )

    return beta


robust_coefficients = robust_linear_fit(
    D_cal,
    Z_cal
)

robust_scale = robust_coefficients[0]
robust_offset = robust_coefficients[1]

robust_cal_pred = (
    robust_scale * D_cal
    + robust_offset
)

robust_val_pred = (
    robust_scale * D_val
    + robust_offset
)

robust_train_mae, robust_train_rmse, _ = calculate_metrics(
    Z_cal,
    robust_cal_pred
)

robust_mae, robust_rmse, robust_r2 = calculate_metrics(
    Z_val,
    robust_val_pred
)


# =================================================
# PRINT CALIBRATION DATA
# =================================================

print("CALIBRATION GCPs")
print("--------------------------------------------")

for _, row in cal.iterrows():

    print(
        f"{row['id']}: "
        f"Depth={row['relative_depth']:.6f} | "
        f"Reference={row['reference_elevation']:.2f}m"
    )


print()
print("VALIDATION GCPs")
print("--------------------------------------------")

for _, row in val.iterrows():

    print(
        f"{row['id']}: "
        f"Depth={row['relative_depth']:.6f} | "
        f"Reference={row['reference_elevation']:.2f}m"
    )


# =================================================
# LINEAR RESULTS
# =================================================

print()
print("============================================")
print("LINEAR REGRESSION")
print("============================================")

print(
    f"Scale  : {linear_scale:.6f}"
)

print(
    f"Offset : {linear_offset:.6f}"
)

print(
    f"Training MAE  : {linear_train_mae:.3f} m"
)

print(
    f"Training RMSE : {linear_train_rmse:.3f} m"
)

print(
    f"Validation MAE  : {linear_mae:.3f} m"
)

print(
    f"Validation RMSE : {linear_rmse:.3f} m"
)

print(
    f"Validation R²   : {linear_r2:.4f}"
)


# =================================================
# POLYNOMIAL RESULTS
# =================================================

print()
print("============================================")
print("POLYNOMIAL REGRESSION (DEGREE 2)")
print("============================================")

print(
    f"Coefficient a : {poly_coefficients[0]:.6f}"
)

print(
    f"Coefficient b : {poly_coefficients[1]:.6f}"
)

print(
    f"Coefficient c : {poly_coefficients[2]:.6f}"
)

print(
    f"Training MAE  : {poly_train_mae:.3f} m"
)

print(
    f"Training RMSE : {poly_train_rmse:.3f} m"
)

print(
    f"Validation MAE  : {poly_mae:.3f} m"
)

print(
    f"Validation RMSE : {poly_rmse:.3f} m"
)

print(
    f"Validation R²   : {poly_r2:.4f}"
)


# =================================================
# ROBUST RESULTS
# =================================================

print()
print("============================================")
print("ROBUST LINEAR REGRESSION")
print("============================================")

print(
    f"Scale  : {robust_scale:.6f}"
)

print(
    f"Offset : {robust_offset:.6f}"
)

print(
    f"Training MAE  : {robust_train_mae:.3f} m"
)

print(
    f"Training RMSE : {robust_train_rmse:.3f} m"
)

print(
    f"Validation MAE  : {robust_mae:.3f} m"
)

print(
    f"Validation RMSE : {robust_rmse:.3f} m"
)

print(
    f"Validation R²   : {robust_r2:.4f}"
)


# =================================================
# VALIDATION PREDICTIONS
# =================================================

print()
print("============================================")
print("INDEPENDENT VALIDATION PREDICTIONS")
print("============================================")

for i in range(len(val)):

    gcp_id = val.iloc[i]["id"]
    reference = Z_val[i]

    print()
    print(f"{gcp_id}")
    print("--------------------------------------------")

    print(
        f"Reference Elevation : {reference:.2f} m"
    )

    print(
        f"Linear Prediction   : {linear_val_pred[i]:.2f} m"
    )

    print(
        f"Polynomial Prediction: {poly_val_pred[i]:.2f} m"
    )

    print(
        f"Robust Prediction   : {robust_val_pred[i]:.2f} m"
    )


# =================================================
# METHOD COMPARISON
# =================================================

results = {

    "Linear": {
        "MAE": linear_mae,
        "RMSE": linear_rmse,
        "R2": linear_r2
    },

    "Polynomial": {
        "MAE": poly_mae,
        "RMSE": poly_rmse,
        "R2": poly_r2
    },

    "Robust": {
        "MAE": robust_mae,
        "RMSE": robust_rmse,
        "R2": robust_r2
    }
}


# =================================================
# SELECT BEST METHOD
#
# Primary criterion:
# Validation RMSE
#
# Secondary criterion:
# Validation MAE
# =================================================

best_method = min(
    results.keys(),
    key=lambda method: (
        results[method]["RMSE"],
        results[method]["MAE"]
    )
)


# =================================================
# FINAL COMPARISON TABLE
# =================================================

print()
print("============================================")
print("FINAL METHOD COMPARISON")
print("============================================")

print()
print(
    f"{'Method':<15}"
    f"{'MAE (m)':>12}"
    f"{'RMSE (m)':>12}"
    f"{'R²':>12}"
)

print("--------------------------------------------")

for method, values in results.items():

    print(
        f"{method:<15}"
        f"{values['MAE']:>12.3f}"
        f"{values['RMSE']:>12.3f}"
        f"{values['R2']:>12.4f}"
    )


# =================================================
# BEST METHOD
# =================================================

print()
print("============================================")
print("BEST METHOD")
print("============================================")

print(
    f"Selected method : {best_method}"
)

print(
    f"Validation MAE  : "
    f"{results[best_method]['MAE']:.3f} m"
)

print(
    f"Validation RMSE : "
    f"{results[best_method]['RMSE']:.3f} m"
)

print(
    f"Validation R²   : "
    f"{results[best_method]['R2']:.4f}"
)


# =================================================
# SCIENTIFIC WARNING
# =================================================

print()
print("============================================")
print("SCIENTIFIC INTERPRETATION")
print("============================================")

if results[best_method]["R2"] < 0:

    print(
        "WARNING: Validation R² is negative."
    )

    print(
        "The current GCP dataset does not demonstrate"
    )

    print(
        "reliable independent metric-elevation accuracy."
    )

else:

    print(
        "Validation R² is non-negative."
    )

    print(
        "Further validation with additional independent"
    )

    print(
        "GCPs is still recommended."
    )


print()
print(
    "Method selection is based on independent"
)

print(
    "validation performance, not training error."
)

print()
print("============================================")
print("COMPARISON COMPLETED")
print("============================================")