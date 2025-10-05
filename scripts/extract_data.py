import os
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from osgeo import gdal
import cv2
import re
import json
import math

# ----------------------------
# User Config
# ----------------------------
VOLUME_URL = "https://planetarydata.jpl.nasa.gov/img/data/mro/ctx/mrox_3866/"
RAW_DIR = r"C:\Users\himan\Desktop\Spaceapps\spaceapps_challenge\data\raw\ctx_mrox_3886"
PROCESSED_DIR = r"C:\Users\himan\Desktop\Spaceapps\spaceapps_challenge\data\processed\ctx_mrox_3886"
METADATA_DIR = r"C:\Users\himan\Desktop\Spaceapps\spaceapps_challenge\data\metadata\ctx_mrox_3886"
WEB_TILES_DIR = r"C:\Users\himan\Desktop\Spaceapps\spaceapps_challenge\web_tiles\ctx_mrox_3886"

DOWNLOAD_LIMIT = 10  # None = download all
DOWNLOAD_DELAY = 1  # seconds between downloads
TILE_SIZE = 256

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
    converted_files = []

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
                converted_files.append(dst_path)
            except Exception as e:
                print(f"Failed to convert {fname}: {e}")
    return converted_files

def extract_lbl_from_img(raw_dir, metadata_dir):
    os.makedirs(metadata_dir, exist_ok=True)
    metadata_list = []

    for fname in os.listdir(raw_dir):
        if not fname.upper().endswith(".IMG"):
            continue
        img_path = os.path.join(raw_dir, fname)
        try:
            header_text = ""
            with open(img_path, "rb") as f:
                while True:
                    line = f.readline().decode(errors="ignore")
                    header_text += line
                    if "END" in line:
                        break

            metadata = {}
            for key in ["PRODUCT_ID", "IMAGE", "LINES", "LINE_SAMPLES", "SAMPLE_TYPE", "SAMPLE_BITS",
                        "START_TIME", "STOP_TIME", "SPACECRAFT_NAME", "INSTRUMENT_NAME",
                        "MISSION_PHASE_NAME", "TARGET_NAME"]:
                m = re.search(rf"{key}\s*=\s*(.+)", header_text)
                if m:
                    metadata[key] = m.group(1).strip()
            metadata["FILE_NAME"] = fname

            json_path = os.path.join(metadata_dir, fname.replace(".IMG", ".json"))
            with open(json_path, "w") as jf:
                json.dump(metadata, jf, indent=4)

            metadata_list.append(metadata)

        except Exception as e:
            print(f"Failed to extract metadata from {fname}: {e}")

    combined_path = os.path.join(metadata_dir, "combined_metadata.json")
    with open(combined_path, "w") as cf:
        json.dump(metadata_list, cf, indent=4)
    print(f"✅ Metadata extracted for {len(metadata_list)} images.")

def create_opencv_tiles(processed_dir, web_tiles_dir, tile_size=256):
    """Use OpenCV to generate pyramid tiles for web display."""
    os.makedirs(web_tiles_dir, exist_ok=True)
    for tif_file in os.listdir(processed_dir):
        if not tif_file.lower().endswith(".tif"):
            continue
        input_tif = os.path.join(processed_dir, tif_file)
        output_dir = os.path.join(web_tiles_dir, tif_file[:-4])
        os.makedirs(output_dir, exist_ok=True)

        img = cv2.imread(input_tif, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Failed to read {input_tif}")
            continue

        h, w = img.shape[:2]
        max_dim = max(h, w)
        max_level = math.ceil(math.log2(max_dim))

        print(f"Creating tiles for {tif_file}: {w}x{h}, Pyramid levels {max_level+1}")

        for level in range(max_level, -1, -1):
            scale = 2 ** (max_level - level)
            new_w = math.ceil(w / scale)
            new_h = math.ceil(h / scale)
            resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

            level_dir = os.path.join(output_dir, f"level_{level}")
            os.makedirs(level_dir, exist_ok=True)

            for y in range(0, new_h, tile_size):
                for x in range(0, new_w, tile_size):
                    tile = resized[y:y+tile_size, x:x+tile_size]
                    tile_name = f"{x}_{y}.jpg"
                    cv2.imwrite(os.path.join(level_dir, tile_name), tile)
    print("✅ OpenCV pyramid tiles created.")

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
    converted = convert_img_to_tif(RAW_DIR, PROCESSED_DIR)
    print(f"Converted {len(converted)} files.")

    print("4️⃣ Extracting metadata from .IMG files...")
    extract_lbl_from_img(RAW_DIR, METADATA_DIR)

    print("5️⃣ Creating OpenCV pyramid tiles...")
    create_opencv_tiles(PROCESSED_DIR, WEB_TILES_DIR, TILE_SIZE)

    print("\n✅ Workflow complete!")
