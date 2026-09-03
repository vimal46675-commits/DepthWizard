import numpy as np
import rasterio

# ============================================
# FILE PATHS
# ============================================

depth_path = "results/depth_maps/test_depth.npy"
dem_path = "data/dem/Copernicus_DSM_30_N25_00_E081_00_DEM.tif"

output_path = "results/depth_maps/calibrated_elevation.npy"


# ============================================
# LOAD DEPTH MAP
# ============================================

print("Loading depth map...")

depth = np.load(depth_path)

print("Depth map loaded successfully.")
print("Shape:", depth.shape)
print("Minimum depth:", float(depth.min()))
print("Maximum depth:", float(depth.max()))
print("Mean depth:", float(depth.mean()))


# ============================================
# GROUND CONTROL POINTS
#
# Format:
# (image_x, image_y, latitude, longitude)
# ============================================

gcp_points = [
    (612, 602, 25.436673, 81.889116),
    (814, 348, 25.436750, 81.889116),
    (135, 430, 25.436779, 81.889213),
    (148, 842, 25.436789, 81.889106),
    (1535, 578, 25.436721, 81.889234),
]


# ============================================
# READ DEM AND EXTRACT ELEVATIONS
# ============================================

print("\nReading Copernicus DEM...")

depth_values = []
elevation_values = []

with rasterio.open(dem_path) as dem:

    print("DEM CRS:", dem.crs)

    # Read DEM once instead of reading it for every GCP
    dem_array = dem.read(1)

    for i, (x, y, lat, lon) in enumerate(gcp_points, start=1):

        # Check image coordinates
        if not (0 <= x < depth.shape[1] and 0 <= y < depth.shape[0]):
            print(
                f"GCP {i}: ERROR - pixel ({x}, {y}) "
                "is outside the image."
            )
            continue

        # Get relative depth value at image pixel
        relative_depth = float(depth[y, x])

        # Convert geographic coordinates to DEM pixel
        row, col = dem.index(lon, lat)

        # Check DEM coordinates
        if not (
            0 <= row < dem_array.shape[0]
            and 0 <= col < dem_array.shape[1]
        ):
            print(
                f"GCP {i}: ERROR - coordinate "
                f"({lat}, {lon}) is outside the DEM."
            )
            continue

        # Get elevation from DEM
        elevation = float(dem_array[row, col])

        # Store values
        depth_values.append(relative_depth)
        elevation_values.append(elevation)

        print(
            f"GCP {i}: "
            f"Pixel=({x}, {y}) | "
            f"Lat={lat} | "
            f"Lon={lon} | "
            f"Depth={relative_depth:.6f} | "
            f"Elevation={elevation:.3f} m"
        )


# ============================================
# CHECK GCP DATA
# ============================================

depth_values = np.array(depth_values)
elevation_values = np.array(elevation_values)

print("\nValid GCPs:", len(depth_values))

if len(depth_values) < 3:
    print("ERROR: At least 3 valid GCPs are required.")
    raise SystemExit

if np.allclose(depth_values, depth_values[0]):
    print(
        "ERROR: All GCP depth values are almost identical. "
        "Calibration cannot be performed reliably."
    )
    raise SystemExit


# ============================================
# LINEAR CALIBRATION
#
# Elevation = Scale × RelativeDepth + Offset
# ============================================

scale, offset = np.polyfit(
    depth_values,
    elevation_values,
    1
)

print("\n============================================")
print("CALIBRATION RESULT")
print("============================================")

print("Scale :", scale)
print("Offset:", offset)

print(
    "\nEquation:"
    "\nElevation = "
    f"{scale:.6f} × RelativeDepth + "
    f"{offset:.6f}"
)


# ============================================
# CALCULATE GCP FIT ERROR
# ============================================

predicted_elevations = (
    scale * depth_values + offset
)

errors = (
    predicted_elevations - elevation_values
)

rmse = np.sqrt(
    np.mean(errors ** 2)
)

print("\nGCP calibration RMSE:", f"{rmse:.3f}", "meters")


# ============================================
# GENERATE CALIBRATED ELEVATION MAP
# ============================================

print("\nGenerating calibrated elevation map...")

elevation_map = (
    scale * depth + offset
)


# ============================================
# SAVE RESULT
# ============================================

np.save(
    output_path,
    elevation_map
)

print("\n============================================")
print("SUCCESS")
print("============================================")

print("Calibrated elevation map saved to:")
print(output_path)

print("\nElevation map statistics:")
print("Minimum:", float(elevation_map.min()), "m")
print("Maximum:", float(elevation_map.max()), "m")
print("Mean   :", float(elevation_map.mean()), "m")