import rasterio
from rasterio.warp import reproject, Resampling
import glob
import numpy as np

# Exact DEM path
dem_file = r"C:\Users\vimal\DepthWizard\Depth-Anything-V2\data\dem\Copernicus_DSM_30_N25_00_E081_00_DEM.tif"

# Automatically find Sentinel-2 TIFF
imagery_files = glob.glob(r".\data\imagery\*")

if not imagery_files:
    raise FileNotFoundError("No imagery file found in data\\imagery")

imagery_file = imagery_files[0]

output_file = r".\data\dem\aligned_to_imagery.tif"

print("Imagery:", imagery_file)
print("DEM:", dem_file)

with rasterio.open(imagery_file) as img:
    with rasterio.open(dem_file) as dem:

        aligned_dem = np.full(
            (img.height, img.width),
            -9999,
            dtype=np.float32
        )

        reproject(
            source=rasterio.band(dem, 1),
            destination=aligned_dem,
            src_transform=dem.transform,
            src_crs=dem.crs,
            dst_transform=img.transform,
            dst_crs=img.crs,
            src_nodata=dem.nodata,
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