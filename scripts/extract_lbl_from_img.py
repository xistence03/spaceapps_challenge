import pvl
img_path = r"C:/Users/himan/Desktop/Spaceapps/spaceapps_challenge/data/raw/ctx/mrox_4122/N20_070273_1355_XI_44S280W.IMG"

def extract_label(img_path):
    """
    Reads the embedded PDS label section from a .IMG file.
    """
    with open(img_path, 'rb') as f:
        label = pvl.load(f)
    return label


if __name__ == "__main__":
    img_file = r"C:/Users/himan/Desktop/Spaceapps/spaceapps_challenge/data/raw/ctx/mrox_4122\N20_070273_1355_XI_44S280W.IMG"
    label = extract_label(img_file)

    print("\n===== LABEL CONTENTS =====\n")
    for key, value in label.items():
        print(f"{key}: {value}")
