import argparse
from pathlib import Path
import numpy as np
from PIL import Image

TOLERANCE = 25 # Tolerance for color distance
DEFAULT_SPRITE_DIR = Path(__file__).resolve().parents[1] / "assets"

def remove_background(img_path, out_path, tolerance=TOLERANCE):
    print(f"Processing {img_path} ...")
    img = Image.open(img_path).convert("RGBA")
    data = np.array(img)
    
    # Get top-left pixel as reference background color
    ref_color = data[0, 0, :3].astype(np.int32)
    
    # Calculate Euclidean distance of RGB channels
    rgb = data[:, :, :3].astype(np.int32)
    diff = rgb - ref_color
    dist = np.sqrt(np.sum(diff**2, axis=2))
    
    # Create mask where distance < TOLERANCE
    mask = dist < tolerance
    
    # Set alpha to 0 for matching pixels
    data[mask, 3] = 0
    
    # Save processed image
    processed_img = Image.fromarray(data)
    processed_img.save(out_path, "PNG")
    print(f"Saved {out_path}")

def parse_args():
    parser = argparse.ArgumentParser(description="批量移除 spritesheet 的纯色背景。")
    parser.add_argument("sprite_dir", nargs="?", type=Path, default=DEFAULT_SPRITE_DIR)
    parser.add_argument("--tolerance", type=float, default=TOLERANCE)
    return parser.parse_args()


def main():
    args = parse_args()
    sprite_dir = args.sprite_dir.resolve()
    if not sprite_dir.is_dir():
        raise SystemExit(f"Sprite directory does not exist: {sprite_dir}")

    files = sorted(sprite_dir.glob("*_spritesheet.png"))
    if not files:
        print(f"No source spritesheets found in {sprite_dir}")
        return
    for source_path in files:
        out_path = source_path.with_name(f"{source_path.stem}_transparent.png")
        remove_background(source_path, out_path, args.tolerance)
        
if __name__ == "__main__":
    main()
