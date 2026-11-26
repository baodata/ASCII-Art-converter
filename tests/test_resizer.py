import unittest
from pathlib import Path
from PIL import Image

import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from python_cli.utils.image_resizer import (
    calculate_ascii_dimensions,
    load_and_preprocess_image,
    get_pixel_matrix,
)


class TestImageResizer(unittest.TestCase):

    # Kiểm tra với ảnh vuông (1:1):
    def test_calculate_ascii_dimensions_square(self):
        w, h = calculate_ascii_dimensions(
            orig_width=100,
            orig_height=100,
            target_width=100,
            aspect_ratio_correction=0.55
        )
        self.assertEqual(w, 100)
        self.assertEqual(h, 55)

    # Kiểm tra với ảnh chữ nhật đứng (9:16):
    def test_calculate_ascii_dimensions_rectangular(self):
        w, h = calculate_ascii_dimensions(
            orig_width=1920,
            orig_height=1080,
            target_width=120,
            aspect_ratio_correction=0.5
        )
        self.assertEqual(w, 120)
        self.assertEqual(h, 34)

    # Kiểm tra với ảnh có chiều cao bằng 0 (không hợp lệ):
    def test_calculate_ascii_dimensions_invalid(self):
        with self.assertRaises(ValueError):
            calculate_ascii_dimensions(0, 100, target_width=80)
        with self.assertRaises(ValueError):
            calculate_ascii_dimensions(100, -5, target_width=80)
        with self.assertRaises(ValueError):
            calculate_ascii_dimensions(100, 100, target_width=0)

    # Kiểm tra với ảnh 200x100 pixel, đỏ
    def test_preprocess_and_matrix_synthetic_image(self):
        img = Image.new("RGB", (200, 100), color=(255, 0, 0))
        
        target_width = 50
        processed_img = load_and_preprocess_image(
            image_source=img,
            target_width=target_width,
            aspect_ratio_correction=0.55,
            to_grayscale=True
        )

        # Kiểm tra chế độ ảnh xám
        self.assertEqual(processed_img.mode, 'L')
        
        # Kiểm tra kích thước sau khi co giãn
        # w = 50, h = round(50 * (100/200) * 0.55) = round(13.75) = 14
        self.assertEqual(processed_img.size, (50, 14))

        # Kiểm tra trích xuất ma trận pixel
        matrix = get_pixel_matrix(processed_img)
        self.assertEqual(len(matrix), 14)       # Số hàng = height
        self.assertEqual(len(matrix[0]), 50)    # Số cột = width

        # Giá trị pixel phải xấp xỉ 76 (độ sáng của màu đỏ thuần)
        for row in matrix:
            for val in row:
                self.assertAlmostEqual(val, 76, delta=2)

    # Kiểm tra với ảnh thực tế từ thư mục assets
    def test_preprocess_with_real_assets(self):
        assets_dir = PROJECT_ROOT / "assets"
        sample_images = ["datdichoi.jpg", "earth.jpg"]

        for img_name in sample_images:
            img_path = assets_dir / img_name
            if img_path.exists():
                processed = load_and_preprocess_image(
                    image_source=img_path,
                    target_width=80,
                    aspect_ratio_correction=0.55
                )
                self.assertEqual(processed.mode, 'L')
                self.assertEqual(processed.size[0], 80)
                self.assertGreater(processed.size[1], 0)

                matrix = get_pixel_matrix(processed)
                self.assertEqual(len(matrix), processed.size[1])
                self.assertEqual(len(matrix[0]), 80)

                # Đảm bảo mọi pixel đều nằm trong khoảng 0..255
                for row in matrix:
                    for pixel in row:
                        self.assertTrue(0 <= pixel <= 255)


if __name__ == "__main__":
    unittest.main()
