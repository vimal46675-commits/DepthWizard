import rasterio

# Path of Copernicus DEM
dem_path = "data/dem/Copernicus_DSM_30_N25_00_E081_00_DEM.tif"

# Triveni Sangam (Jhunsi) coordinates
lat = 25.4294
lon = 81.9017

with rasterio.open(dem_path) as src:
    row, col = src.index(lon, lat)
    elevation = src.read(1)[row, col]

print("Location:", lat, lon)
print("Ground elevation (meters):", elevation)