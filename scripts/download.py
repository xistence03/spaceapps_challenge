import os
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# ----------------------------
# User Config
# ----------------------------
VOLUME_URL = "https://planetarydata.jpl.nasa.gov/img/data/mro/ctx/mrox_4099/"
RAW_DIR = "C:/Users/himan/Desktop/Spaceapps/spaceapps_challenge/data/raw/ctx/mrox_4099"
DOWNLOAD_LIMIT = 5  # only first 5 files
DOWNLOAD_DELAY = 1   # seconds between downloads

# ----------------------------
# Functions
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
             if a['href'].upper().endswith(".IMG")]
    return links

def download_files(links, dest_folder, limit=5, delay=1):
    os.makedirs(dest_folder, exist_ok=True)
    links = links[:limit]
    for link in tqdm(links, desc="Downloading .IMG files"):
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

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    print("1️⃣ Getting .IMG file links...")
    links = get_img_links(VOLUME_URL)
    print(f"Found {len(links)} .IMG files.")
    
    if not links:
        print("No .IMG files found. Exiting.")
        exit()

    print(f"2️⃣ Downloading first {DOWNLOAD_LIMIT} .IMG files...")
    download_files(links, RAW_DIR, limit=DOWNLOAD_LIMIT, delay=DOWNLOAD_DELAY)

    print("\n✅ Download complete!")
