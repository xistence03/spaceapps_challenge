import os
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from osgeo import gdal
import rasterio
from rasterio.windows import Window

# ----------------------------
# User Config
# ----------------------------
VOLUME_URL = "https://planetarydata.jpl.nasa.gov/img/data/mro/ctx/mrox_4103/"
RAW_DIR = "C:/Users/himan/Desktop/Spaceapps/spaceapps_challenge/data/raw/ctx/mrox_4103"
PROCESSED_DIR = "C:/Users/himan/Desktop/Spaceapps/spaceapps_challenge/data/processed/ctx_mrox_4103"
TILE_DIR = "C:/Users/himan/Desktop/Spaceapps/spaceapps_challenge/data/tiles/ctx_mrox_4103"
TILE_SIZE = 512
DOWNLOAD_LIMIT = 5  # Set None to download all files
DOWNLOAD_DELAY = 1  # seconds between downloads

# Enable GDAL exceptions
gdal.UseExceptions()

# ----------------------------
# Helper Functions
# ----------------------------

def get_img_links(volume_url):
    if not volume_url.endswith('/'):
        volume_url += '/'
    data_url = volume_url + "data/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(data_url, headers=headers, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error accessing {data_url}: {e}")
        return []
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = [data_url + a['href'] for a in soup.find_all('a', href=True)
             if a['href'].upper().endswith(('.IMG', '.LBL'))]
    return links

def download_files(links, dest_folder, limit=None, delay=1):
    os.makedirs(dest_folder, exist_ok=True)
    if limit:
        links = links[:limit]
    for link in tqdm(links, desc="Downloading files"):
        fname = os.path.join(dest_folder, os.path.basename(link))
        if os.path.exists(fname):
            continue
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(link, stream=True, headers=headers, timeout=30)
            with open(fname, 'wb') as f:
                for chunk in resp.iter_content(1024):
                    if chunk:
                        f.write(chunk)
            time.sleep(delay)
        except Exception as e:
            print(f"Error downloading {link}: {e}")

def convert_img_to_tif(raw_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for fname in os.listdir(raw_dir):
        if fname.upper().endswith(".IMG"):
            src_path = os.path.join(raw_dir, fname)
            dst_path = os.path.join(out_dir, fname.replace(".IMG", ".tif"))
            print(f"Converting {fname} → {dst_path}")
            try:
                gdal.Translate(
                    dst_path,
                    src_path,
                    options=gdal.TranslateOptions(format='GTiff', creationOptions=['BIGTIFF=YES'])
                )
            except Exception as e:
                print(f"Failed to convert {fname}: {e}")

def tile_tifs(processed_dir, tile_dir, tile_size=512):
    os.makedirs(tile_dir, exist_ok=True)
    for fname in os.listdir(processed_dir):
        if fname.lower().endswith(".tif"):
            path = os.path.join(processed_dir, fname)
            try:
                with rasterio.open(path) as src:
                    for i in range(0, src.width, tile_size):
                        for j in range(0, src.height, tile_size):
                            w = min(tile_size, src.width - i)
                            h = min(tile_size, src.height - j)
                            window = Window(i, j, w, h)
                            transform = src.window_transform(window)
                            tile = src.read(1, window=window)
                            profile = src.profile
                            profile.update({"width": w, "height": h, "transform": transform})
                            out_name = f"{fname[:-4]}_tile_{i}_{j}.tif"
                            out_path = os.path.join(tile_dir, out_name)
                            with rasterio.open(out_path, "w", **profile) as dst:
                                dst.write(tile, 1)
            except Exception as e:
                print(f"Failed to tile {fname}: {e}")

# ----------------------------
# Main Workflow
# ----------------------------
if __name__ == "__main__":
    print("1️⃣ Getting file links...")
    links = get_img_links(VOLUME_URL)
    print(f"Found {len(links)} files.")

    if not links:
        print("No files found. Exiting.")
        exit()

    print("2️⃣ Downloading files...")
    download_files(links, RAW_DIR, limit=DOWNLOAD_LIMIT, delay=DOWNLOAD_DELAY)

    print("3️⃣ Converting .IMG → .tif...")
    convert_img_to_tif(RAW_DIR, PROCESSED_DIR)

    print("4️⃣ Tiling .tif images...")
    tile_tifs(PROCESSED_DIR, TILE_DIR, TILE_SIZE)

    print("\n✅ Workflow complete!")
