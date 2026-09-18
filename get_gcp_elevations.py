import rasterio

DEM_PATH = r"data\dem\Copernicus_DSM_30_N25_00_E081_00_DEM.tif"

# New GCP coordinates from the latest 12 selected image points
gcp_points = [
    (25.894066, 81.081713),
    (25.855137, 81.439668),
    (25.832551, 81.657800),
    (25.406091, 81.022222),
    (25.316451, 81.130403),
    (25.265718, 81.343275),
    (25.307147, 81.685831),
    (25.479211, 81.835132),
    (25.948880, 81.727558),
    (26.095082, 81.900554),
    (26.099279, 82.066282),
    (25.828751, 82.056863),
]

print("============================================")
print("GCP ELEVATION EXTRACTION")
print("============================================")

with rasterio.open(DEM_PATH) as dem:

    print("DEM CRS:", dem.crs)
    print()

    dem_array = dem.read(1)

    for i, (lat, lon) in enumerate(gcp_points, start=1):

        row, col = dem.index(lon, lat)

        if (
            0 <= row < dem.height
            and 0 <= col < dem.width
        ):

            elevation = float(dem_array[row, col])

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