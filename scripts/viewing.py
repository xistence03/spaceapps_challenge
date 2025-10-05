import rasterio
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt

# Path to a converted .tif
tif_path = r"C:\Users\himan\Desktop\Spaceapps\spaceapps_challenge\data\merged\ctx_mrox_3886_basemap.tif"

with rasterio.open(tif_path) as src:
    img = src.read(1)  # read first band
    height, width = img.shape
    dpi = 100  # dots per inch
    figsize = (width / dpi, height / dpi)
    plt.figure(figsize=figsize)
    plt.imshow(img, cmap='gray')
    plt.title("Preview of CTX .tif")
    plt.axis('off')
    plt.savefig("preview.png", dpi=300, bbox_inches='tight')
    print("Preview saved to preview.png")

