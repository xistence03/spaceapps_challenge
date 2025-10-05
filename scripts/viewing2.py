import os
from osgeo import gdal
import matplotlib.pyplot as plt

input_tif = r"C:\Users\himan\Desktop\Spaceapps\spaceapps_challenge\data\merged\ctx_mrox_3886_basemap.tif"

ds = gdal.Open(input_tif)

# Read into a small downsampled array (max 2000x2000 for preview)
w, h = ds.RasterXSize, ds.RasterYSize
scale = max(w, h) / 2000  # adjust max dimension to 2000 pixels
read_w = int(w / scale)
read_h = int(h / scale)

band = ds.GetRasterBand(1)
preview = band.ReadAsArray(buf_xsize=read_w, buf_ysize=read_h)

plt.imshow(preview, cmap='gray')
plt.axis('off')
output_folder = r"C:\Users\himan\Desktop\Spaceapps\spaceapps_challenge\previews"
os.makedirs(output_folder, exist_ok=True)  # create folder if it doesn't exist
output_file = os.path.join(output_folder, "preview_downsampled.png")
plt.savefig(output_file, dpi=150, bbox_inches='tight')
plt.close()
print("✅ Preview saved as preview_downsampled.png")
