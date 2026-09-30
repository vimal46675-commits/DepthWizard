import rasterio

dem_path = "data/dem/Copernicus_DSM_30_N25_00_E081_00_DEM.tif"

with rasterio.open(dem_path) as dem:
    print("=== COPERNICUS DEM ===")
    print("CRS:", dem.crs)
    print("Width:", dem.width)
    print("Height:", dem.height)
    print("Resolution:", dem.res)
    print("Bounds:")
    print("  Left:", dem.bounds.left)
    print("  Right:", dem.bounds.right)
    print("  Bottom:", dem.bounds.bottom)
    print("  Top:", dem.bounds.top)

    data = dem.read(1)

    print("\nElevation:")
    print("  Minimum:", float(data.min()), "m")
    print("  Maximum:", float(data.max()), "m")
    print("  Mean:", float(data.mean()), "m")