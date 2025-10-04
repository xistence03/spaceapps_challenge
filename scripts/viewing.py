import rasterio
import matplotlib.pyplot as plt

# Path to a converted .tif
tif_path = r"C:/Users/himan/Desktop/Spaceapps/spaceapps_challenge/data/processed/ctx_mrox_4099/N19_069594_2620_XN_82N134W.tif"

with rasterio.open(tif_path) as src:
    img = src.read(1)  # read first band
    plt.figure(figsize=(10,10))
    plt.imshow(img, cmap='gray')
    plt.title("Preview of CTX .tif")
    plt.axis('off')
    plt.show()
