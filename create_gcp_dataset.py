import csv

OUTPUT = r"results\gcp_dataset.csv"

gcp_data = [
    ["GCP1", 153, 673, 153, 673, 1.079552, 109.75],
    ["GCP2", 822, 752, 822, 752, 1.508826, 108.48],
    ["GCP3", 1230, 797, 1230, 797, 1.739009, 101.18],
    ["GCP4", 42, 1681, 42, 1681, 2.334853, 97.71],
    ["GCP5", 245, 1866, 245, 1866, 2.540169, 111.08],
    ["GCP6", 645, 1970, 645, 1970, 2.676443, 111.59],
    ["GCP7", 1288, 1882, 1288, 1882, 2.781346, 97.14],
    ["GCP8", 1566, 1525, 1566, 1525, 2.493215, 83.74],
    ["GCP9", 1359, 556, 1359, 556, 1.587470, 101.13],
]

print("============================================")
print("GCP DATASET CREATION - 9 VALID GCPs")
print("============================================")

with open(OUTPUT, "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "id",
        "original_x",
        "original_y",
        "depth_x",
        "depth_y",
        "relative_depth",
        "reference_elevation"
    ])

    for row in gcp_data:

        writer.writerow(row)

        print(
            f"{row[0]}: "
            f"Depth Pixel=({row[3]},{row[4]}) | "
            f"Depth={row[5]:.6f} | "
            f"Elevation={row[6]:.2f}m"
        )

print()
print("============================================")
print("DATASET CREATED SUCCESSFULLY")
print("============================================")
print(f"Output: {OUTPUT}")
print(f"Valid GCPs: {len(gcp_data)}")
print("============================================")