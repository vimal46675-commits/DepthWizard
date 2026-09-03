import os
import numpy as np
import rasterio

# ============================================
# FILE PATHS
# ============================================

depth_path = os.path.join("results", "depth_maps", "test_depth.npy")
dem_path = os.path.join("data", "dem", "Copernicus_DSM_30_N25_00_E081_00_DEM.tif")
output_path = os.path.join("results", "depth_maps", "calibrated_elevation.npy")


def calibrate_depth_with_gcps(depth_values, elevation_values):
    """
    Calculates linear calibration parameters from corresponding relative depth
    and reference elevation values.
    
    Elevation = Scale * RelativeDepth + Offset
    """
    depth_values = np.array(depth_values, dtype=np.float64)
    elevation_values = np.array(elevation_values, dtype=np.float64)

    num_gcps = len(depth_values)

    if num_gcps < 3:
        print("ERROR: Calibration requires at least 3 valid GCP pairs.")
        print("Calibration cannot currently be performed.")
        return None

    if np.allclose(depth_values, depth_values[0]):
        print("ERROR: All relative depth values are identical.")
        print("Calibration cannot currently be performed.")
        return None

    # Fit linear calibration model: Elevation = Scale * RelativeDepth + Offset
    scale, offset = np.polyfit(depth_values, elevation_values, 1)

    # Calculate RMSE
    predicted_elevations = scale * depth_values + offset
    errors = predicted_elevations - elevation_values
    rmse = float(np.sqrt(np.mean(errors ** 2)))

    print("\n============================================")
    print("MEMBER 2 CALIBRATION REPORT")
    print("============================================")
    print(f"Number of GCPs used : {num_gcps}")
    print(f"Scale               : {scale:.6f}")
    print(f"Offset              : {offset:.6f}")
    print(f"Equation            : Elevation = {scale:.6f} * RelativeDepth + ({offset:.6f})")
    print(f"Calibration RMSE    : {rmse:.3f} meters")

    return {
        "scale": scale,
        "offset": offset,
        "rmse": rmse,
        "num_gcps": num_gcps
    }


def main(gcp_points=None):
    """
    Main calibration module. Accepts a list of user-provided GCP tuples:
    gcp_points = [(image_x, image_y, latitude, longitude), ...]
    """
    print("============================================")
    print("MEMBER 2 GEOSPATIAL CALIBRATION MODULE")
    print("============================================")

    if not os.path.exists(depth_path):
        print(f"ERROR: Depth map file not found: {depth_path}")
        print("Calibration cannot currently be performed.")
        return

    print("Loading relative depth map...")
    depth = np.load(depth_path)
    print(f"Depth map shape: {depth.shape}")
    print(f"Depth min: {depth.min():.4f}, max: {depth.max():.4f}, mean: {depth.mean():.4f}")

    if not gcp_points:
        print("\n--------------------------------------------")
        print("NOTICE: No user-provided GCP data available.")
        print("Calibration cannot currently be performed.")
        print("--------------------------------------------")
        return

    depth_values = []
    elevation_values = []

    if not os.path.exists(dem_path):
        print(f"ERROR: DEM file not found: {dem_path}")
        print("Calibration cannot currently be performed.")
        return

    with rasterio.open(dem_path) as dem:
        dem_array = dem.read(1)

        for i, (x, y, lat, lon) in enumerate(gcp_points, start=1):
            if not (0 <= x < depth.shape[1] and 0 <= y < depth.shape[0]):
                print(f"GCP {i}: Pixel ({x}, {y}) outside image bounds.")
                continue

            row, col = dem.index(lon, lat)
            if not (0 <= row < dem_array.shape[0] and 0 <= col < dem_array.shape[1]):
                print(f"GCP {i}: Coordinate ({lat}, {lon}) outside DEM bounds.")
                continue

            rel_depth = float(depth[y, x])
            elev = float(dem_array[row, col])

            depth_values.append(rel_depth)
            elevation_values.append(elev)

            print(f"GCP {i}: Pixel=({x}, {y}) | Lat={lat:.6f}, Lon={lon:.6f} | Depth={rel_depth:.4f} | Elev={elev:.2f}m")

    result = calibrate_depth_with_gcps(depth_values, elevation_values)

    if result is None:
        return

    scale = result["scale"]
    offset = result["offset"]

    # Generate calibrated elevation map
    print("\nGenerating calibrated elevation map...")
    calibrated_elevation = scale * depth + offset

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    np.save(output_path, calibrated_elevation)

    print(f"Calibrated elevation map saved to: {output_path}")
    print(f"Elevation Min: {calibrated_elevation.min():.2f}m | Max: {calibrated_elevation.max():.2f}m | Mean: {calibrated_elevation.mean():.2f}m")


if __name__ == "__main__":
    # By default, no hardcoded GCP points are assumed.
    # Users can provide gcp_points to run calibration:
    # example: main(gcp_points=[(x1, y1, lat1, lon1), ...])
    main(gcp_points=None)