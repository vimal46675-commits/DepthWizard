import rasterio

DEM_PATH = r"data\dem\Copernicus_DSM_30_N25_00_E081_00_DEM.tif"

# GCP coordinates obtained from Sentinel image
gcp_points = [
    (25.887292, 81.084903),
    (25.451064, 81.015268),
    (25.249586, 81.166973),
    (25.251072, 81.665358),
    (25.252070, 82.000684),
    (25.948536, 81.458791),
    (25.822016, 81.828443),
    (25.670270, 82.008433),
]

print("============================================")
print("GCP ELEVATION EXTRACTION")
print("============================================")

with rasterio.open(DEM_PATH) as dem:

    print("DEM CRS:", dem.crs)
    print()

    for i, (lat, lon) in enumerate(gcp_points, start=1):

        row, col = dem.index(lon, lat)

        if (
            0 <= row < dem.height
            and 0 <= col < dem.width
        ):
            elevation = float(dem.read(1)[row, col])

            print(
                f"GCP {i}: "
                f"Lat={lat:.6f}, "
                f"Lon={lon:.6f}, "
                f"Elevation={elevation:.2f} m"
            )

        else:
            print(
                f"GCP {i}: "
                f"({lat:.6f}, {lon:.6f}) "
                f"OUTSIDE DEM"
            )

print()
print("============================================")
print("DONE")
print("============================================")