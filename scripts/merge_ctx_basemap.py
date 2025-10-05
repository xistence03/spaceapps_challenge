import os
import json
import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.transform import from_origin

# ----------------------------
# User Config
# ----------------------------
PROCESSED_DIR = r"C:\Users\himan\Desktop\Spaceapps\spaceapps_challenge\data\processed\ctx_mrox_3886"
METADATA_DIR = r"C:\Users\himan\Desktop\Spaceapps\spaceapps_challenge\data\metadata\ctx_mrox_3886"
OUTPUT_PATH = r"C:\Users\himan\Desktop\Spaceapps\spaceapps_challenge\data\merged\ctx_mrox_3886_basemap.tif"

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ----------------------------
# Helper Functions
# ----------------------------
def load_metadata(metadata_dir):
    """Load metadata JSON files for each image"""
    meta_files = [f for f in os.listdir(metadata_dir) if f.endswith(".json")]
    metadata = {}
    for mf in meta_files:
        path = os.path.join(metadata_dir, mf)
        with open(path, 'r') as f:
            data = json.load(f)
            img_name = mf.replace(".json", ".tif")
            metadata[img_name] = data
    return metadata

def open_rasters(processed_dir, metadata):
    """Open raster files and fix upside-down images"""
    src_files = []
    for fname in sorted(os.listdir(processed_dir)):
        if fname.lower().endswith(".tif") and fname in metadata:
            path = os.path.join(processed_dir, fname)
            src = rasterio.open(path)
            # Fix negative pixel height if needed
            if src.transform.e < 0:  # upside down
                print(f"[FIX] Flipping {fname}")
                arr = src.read(1)[::-1, :]
                profile = src.profile.copy()
                profile['transform'] = from_origin(0, 0, 1, 1)  # dummy transform
                fixed_path = os.path.join(processed_dir, fname.replace(".tif", "_fixed.tif"))
                with rasterio.open(fixed_path, 'w', **profile) as dst:
                    dst.write(arr, 1)
                src = rasterio.open(fixed_path)
            src_files.append(src)
    return src_files

# ----------------------------
# Main Workflow
# ----------------------------
if __name__ == "__main__":
    print("1️⃣ Loading metadata...")
    metadata = load_metadata(METADATA_DIR)
    print(f"Loaded metadata for {len(metadata)} images.")

    print("2️⃣ Opening rasters...")
    src_files_to_mosaic = open_rasters(PROCESSED_DIR, metadata)
    print(f"✅ {len(src_files_to_mosaic)} TIFFs ready for merging.")

    print("3️⃣ Merging rasters...")
    try:
        # We pass method='first' to handle overlaps
        mosaic, out_trans = merge(src_files_to_mosaic, method='first')
    except Exception as e:
        print("⚠️ Merge failed:", e)
        print("Attempting manual stacking for visualization...")

        # Manual stacking fallback: create canvas large enough for all images
        # Approximate layout based on image order
        widths = [src.width for src in src_files_to_mosaic]
        heights = [src.height for src in src_files_to_mosaic]
        total_width = sum(widths)
        max_height = max(heights)

        mosaic = np.zeros((max_height, total_width), dtype=src_files_to_mosaic[0].read(1).dtype)
        current_x = 0
        for src in src_files_to_mosaic:
            arr = src.read(1)
            mosaic[0:arr.shape[0], current_x:current_x+arr.shape[1]] = arr
            current_x += arr.shape[1]
        out_trans = from_origin(0, 0, 1, 1)

    print(f"4️⃣ Writing merged basemap to {OUTPUT_PATH}...")
    profile = src_files_to_mosaic[0].profile.copy()
    profile.update({
        "height": mosaic.shape[0],
        "width": mosaic.shape[1],
        "transform": out_trans,
        "driver": "GTiff",
        "compress": "lzw"
    })

    with rasterio.open(OUTPUT_PATH, 'w', **profile) as dst:
        dst.write(mosaic, 1)

    print("✅ Basemap merge complete!")
