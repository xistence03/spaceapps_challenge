import os
import rasterio
import matplotlib.pyplot as plt

processed_dir = r"C:/Users/himan/Desktop/Spaceapps/spaceapps_challenge/data/raw/ctx/mrox_4099"

# Get list of .tif files
tif_files = [f for f in os.listdir(processed_dir) if f.lower().endswith(".tif")]

if not tif_files:
    print("No .tif files found in the folder.")
    exit()

# Use the first available file
tif_path = os.path.join(processed_dir, tif_files[0])

with rasterio.open(tif_path) as src:
    img = src.read(1)
    plt.figure(figsize=(10, 10))
    plt.imshow(img, cmap='gray')
    plt.title(f"Preview: {tif_files[0]}")
    plt.axis('off')
    plt.show()
