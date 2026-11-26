from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image
from python_cli.utils.image_resizer import (
    calculate_ascii_dimensions,
    load_and_preprocess_image,
    get_pixel_matrix,
)

def run_visual_test(image_path: Path, target_width: int = 70):
    print(f"ảnh: {image_path.name}")

    original_img = Image.open(image_path)
    orig_w, orig_h = original_img.size
    print(f"    - Kích thước: {orig_w} x {orig_h} (Pixel)")
    print(f"    - Hệ màu: {original_img.mode}")
    print(f"    - Tỷ lệ gốc (Cao / Rộng): {orig_h / orig_w:.3f}")

    new_w, new_h = calculate_ascii_dimensions(
        orig_width=orig_w,
        orig_height=orig_h,
        target_width=target_width,
        aspect_ratio_correction=0.55
    )
    print(f"\nAspect Ratio Correction = 0.55:")
    print(f"    - Chiều rộng mới: {new_w} ký tự")
    print(f"    - Chiều cao mới: {new_h} dòng")
    print(f"    - Tỷ lệ hiển thị thực tế: {new_h / new_w:.3f}")

    processed_img = load_and_preprocess_image(
        image_source=image_path,
        target_width=target_width,
        aspect_ratio_correction=0.55,
        to_grayscale=True
    )
    matrix = get_pixel_matrix(processed_img)

    density_ramp = " .:-=+*#%@"
    ascii_rows = []
    for row in matrix:
        chars = []
        for pixel in row:
            # Ánh xạ từ [0..255] vào chỉ số [0..len(density_ramp)-1]
            index = int((pixel / 255) * (len(density_ramp) - 1))
            chars.append(density_ramp[index])
        ascii_rows.append("".join(chars))

    ascii_art = "\n".join(ascii_rows)

    print(ascii_art)

    # 6. Xuất ra file tests/output_preview.txt
    output_file = PROJECT_ROOT / "tests" / f"output_{image_path.stem}_preview.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"ẢNH NGUỒN: {image_path.name}\n")
        f.write(f"KÍCH THƯỚC: {new_w}x{new_h}\n")
        f.write("=" * new_w + "\n")
        f.write(ascii_art)
        f.write("\n" + "=" * new_w + "\n")


if __name__ == "__main__":
    assets_dir = PROJECT_ROOT / "assets"
    earth_path = assets_dir / "datdichoi.jpg"
    
    if earth_path.exists():
        run_visual_test(earth_path, target_width=70)
    else:
        print("Không tìm thấy ảnh assets/earth.jpg để chạy thử nghiệm.")
