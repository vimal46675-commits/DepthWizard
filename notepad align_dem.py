import rasterio
from rasterio.warp import reproject, Resampling
import glob
import numpy as np

# Find files automatically
imagery_file = glob.glob(r".\data\imagery\*")[0]
dem_file = glob.glob(r".\data\dem\*.tif")[0]

output_file = r".\data\dem\aligned_to_imagery.tif"

# Open Sentinel-2 imagery
with rasterio.open(imagery_file) as img:

    # Open DEM
    with rasterio.open(dem_file) as dem:

        # Create an empty array matching the imagery grid
        aligned_dem = np.empty(
            (img.height, img.width),
            dtype=np.float32
        )

        # Reproject/resample DEM onto imagery grid
        reproject(
            source=rasterio.band(dem, 1),
            destination=aligned_dem,
            src_transform=dem.transform,
            src_crs=dem.crs,
            dst_transform=img.transform,
            dst_crs=img.crs,
            resampling=Resampling.bilinear
        )

        # Use imagery's geospatial metadata
        profile = img.profile.copy()

        profile.update(
            driver="GTiff",
            count=1,
            dtype="float32",
            nodata=-9999
        )

        # Save aligned DEM
        with rasterio.open(output_file, "w", **profile) as dst:
            dst.write(aligned_dem, 1)

print("Aligned DEM created successfully.")
print("Output:", output_file)
print("Grid size:", img.width, "x", img.height)