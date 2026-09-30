from PIL import Image
import matplotlib.pyplot as plt

image_path = "input/test.jpg"

img = Image.open(image_path)

print("Image size:", img.size)
print("\nClick 3–5 clearly identifiable points on the image.")
print("Close the image window when finished.")

plt.figure(figsize=(14, 8))
plt.imshow(img)
plt.title("Click GCP points")
plt.xlabel("X pixel")
plt.ylabel("Y pixel")

points = plt.ginput(
    n=5,
    timeout=0
)

plt.close()

print("\nSelected GCP pixel coordinates:")

for i, (x, y) in enumerate(points, 1):
    print(f"GCP {i}: x={round(x)}, y={round(y)}")