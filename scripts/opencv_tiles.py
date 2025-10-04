import cv2
import os
import math

input_tif = r"C:/Users/himan/Desktop/Spaceapps/spaceapps_challenge/data/processed/ctx_mrox_4103/N19_069692_1920_XN_12N264W.tif"
output_dir = r"C:/Users/himan/Desktop/Spaceapps/spaceapps_challenge/web_tiles/N19_069692_1920_XN_12N264W"
tile_size = 256

os.makedirs(output_dir, exist_ok=True)

# Load image
img = cv2.imread(input_tif, cv2.IMREAD_UNCHANGED)
h, w = img.shape[:2]

# Determine max pyramid level
max_dim = max(h, w)
max_level = math.ceil(math.log2(max_dim))

print(f"Image size: {w}x{h}, Pyramid levels: {max_level+1}")

# Generate pyramid tiles
min_level = 5   # skip tiny base levels
for level in range(max_level, min_level - 1, -1):
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
            
print("✅ Pyramid tiles created.")
