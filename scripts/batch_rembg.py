import argparse
from pathlib import Path
from PIL import Image
import rembg
import io

DEFAULT_SPRITE_DIR = Path(__file__).resolve().parents[1] / "assets"

def remove_background(img_path, out_path):
    print(f"Processing {img_path} with rembg ...")
    try:
        img = Image.open(img_path).convert("RGBA")
        
        # Calculate target height (e.g. 250px per frame * 3 rows = 750px total)
        # We'll use 1500px total to keep some extra sharpness (500px per frame)
        target_height = 1500
        aspect_ratio = img.width / img.height
        target_width = int(target_height * aspect_ratio)
        
        # Resize image for much faster and safer processing
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Convert to bytes for rembg
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='PNG')
        input_data = byte_arr.getvalue()
        
        # Remove background
        output_data = rembg.remove(input_data)
        
        with open(out_path, 'wb') as o:
            o.write(output_data)
            
        print(f"Saved {out_path}")
        return True
    except Exception as e:
        print(f"Failed to process {img_path}: {e}")
        return False

def parse_args():
    parser = argparse.ArgumentParser(description="使用 rembg 批量处理 spritesheet。")
    parser.add_argument("sprite_dir", nargs="?", type=Path, default=DEFAULT_SPRITE_DIR)
    return parser.parse_args()


def main():
    sprite_dir = parse_args().sprite_dir.resolve()
    if not sprite_dir.is_dir():
        raise SystemExit(f"Sprite directory does not exist: {sprite_dir}")
    files = sorted(sprite_dir.glob("*_spritesheet.png"))
    if not files:
        print(f"No source spritesheets found in {sprite_dir}")
        return
    failures = 0
    for source_path in files:
        out_path = source_path.with_name(f"{source_path.stem}_transparent.png")
        failures += not remove_background(source_path, out_path)
    if failures:
        raise SystemExit(f"Failed to process {failures} spritesheet(s).")
        
if __name__ == "__main__":
    main()
