import os
import numpy as np
import rasterio

def inspect_raster(raster_path):
    if not os.path.exists(raster_path):
        raise FileNotFoundError(f"Raster file not found: {raster_path}")

    print("==================================================")
    print("GEOSPATIAL RASTER INSPECTION REPORT")
    print("==================================================")

    with rasterio.open(raster_path) as src:
        # Basic raster metadata
        print(f"1. File path          : {os.path.abspath(raster_path)}")
        print(f"2. Width              : {src.width} pixels")
        print(f"3. Height             : {src.height} pixels")
        print(f"4. Number of bands    : {src.count}")
        print(f"5. Data type          : {src.dtypes[0]}")
        print(f"6. CRS                : {src.crs}")
        print(f"7. Bounds             : {src.bounds}")
        print(f"8. Resolution         : {src.res}")
        print(f"9. Affine transform   :\n{src.transform}")
        print(f"10. NoData value      : {src.nodata}")

        # Read first band data
        data = src.read(1)

        # Handle NoData filtering (excluding -9999 and dataset nodata)
        nodata = src.nodata
        if nodata is not None:
            if np.isnan(nodata):
                valid_mask = ~np.isnan(data)
            else:
                valid_mask = (data != nodata) & (data != -9999) & (~np.isnan(data))
        else:
            valid_mask = (data != -9999) & (~np.isnan(data))

        valid_pixels = data[valid_mask]
        num_valid = len(valid_pixels)

        print("--------------------------------------------------")
        print("ELEVATION STATISTICS (EXCLUDING NODATA)")
        print("--------------------------------------------------")
        print(f"11. Valid pixels count: {num_valid} / {data.size}")

        if num_valid > 0:
            print(f"12. Minimum elevation : {float(np.min(valid_pixels)):.3f} m")
            print(f"13. Maximum elevation : {float(np.max(valid_pixels)):.3f} m")
            print(f"14. Mean elevation    : {float(np.mean(valid_pixels)):.3f} m")
        else:
            print("12. Minimum elevation : No valid pixels")
            print("13. Maximum elevation : No valid pixels")
            print("14. Mean elevation    : No valid pixels")

    print("==================================================")

if __name__ == "__main__":
    target_raster = os.path.join("data", "dem", "aligned_to_imagery.tif")
    inspect_raster(target_raster)
