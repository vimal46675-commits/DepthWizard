import rasterio

image_path = (
    "data/imagery/"
    "2026-07-28-00_00_2026-07-28-23_59_"
    "Sentinel-2_L2A_True_Color.TIF"
)

print("======================================")
print("SENTINEL-2 TIFF INSPECTION")
print("======================================")

with rasterio.open(image_path) as src:

    print("Width:", src.width)
    print("Height:", src.height)
    print("Bands:", src.count)

    print("\nCRS:")
    print(src.crs)

    print("\nResolution:")
    print(src.res)

    print("\nBounds:")
    print("Left  :", src.bounds.left)
    print("Right :", src.bounds.right)
    print("Bottom:", src.bounds.bottom)
    print("Top   :", src.bounds.top)

    print("\nTransform:")
    print(src.transform)

    print("\nData type:")
    print(src.dtypes)

    print("\nCoordinate system details:")
    print(src.crs.to_string())

print("\n======================================")
print("INSPECTION COMPLETE")
print("======================================")