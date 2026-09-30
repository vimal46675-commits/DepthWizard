import os
import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np

# Relative DEM and imagery paths
dem_file = os.path.join("data", "dem", "Copernicus_DSM_30_N25_00_E081_00_DEM.tif")
imagery_file = os.path.join(
    "data",
    "imagery",
    "2026-09-03-00_00_2026-09-03-23_59_Sentinel-2_L2A_True_color.tiff"
)
output_file = os.path.join("data", "dem", "aligned_to_imagery.tif")

if not os.path.exists(imagery_file):
    raise FileNotFoundError(f"Target imagery file not found: {imagery_file}")

if not os.path.exists(dem_file):
    raise FileNotFoundError(f"DEM file not found: {dem_file}")

print("Imagery:", imagery_file)
print("DEM:", dem_file)

with rasterio.open(imagery_file) as img:
    with rasterio.open(dem_file) as dem:

        aligned_dem = np.full(
            (img.height, img.width),
            -9999,
            dtype=np.float32
        )

        src_nodata = dem.nodata if dem.nodata is not None else -9999

        reproject(
            source=rasterio.band(dem, 1),
            destination=aligned_dem,
            src_transform=dem.transform,
            src_crs=dem.crs,
            dst_transform=img.transform,
            dst_crs=img.crs,
            src_nodata=src_nodata,
            dst_nodata=-9999,
            resampling=Resampling.bilinear
        )

        profile = img.profile.copy()

        profile.update(
            driver="GTiff",
            count=1,
            dtype="float32",
            nodata=-9999
        )

        with rasterio.open(output_file, "w", **profile) as dst:
            dst.write(aligned_dem, 1)

        print("Aligned DEM created successfully.")
        print("Output:", output_file)
        print("Grid size:", img.width, "x", img.height)