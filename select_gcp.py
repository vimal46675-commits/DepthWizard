from PIL import Image
import matplotlib.pyplot as plt

image_path = "input/test.jpg"

img = Image.open(image_path)

print("Image size:", img.size)
print()
print("Select 8 clearly identifiable points.")
print("Try to spread the points across the whole image.")
print("After selecting all 8 points, close the image window.")

plt.figure(figsize=(16, 9))
plt.imshow(img)
plt.title("Select 8 GCP Points")
plt.xlabel("X pixel")
plt.ylabel("Y pixel")

points = plt.ginput(n=8, timeout=0)

plt.close()

print("\n===================================")
print("SELECTED GCP PIXEL COORDINATES")
print("===================================")

for i, (x, y) in enumerate(points, 1):
    print(f"GCP {i}: X={round(x)}, Y={round(y)}")