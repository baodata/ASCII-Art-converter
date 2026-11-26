"""
Pre-processing:
1. Tính toán kích thước ảnh ASCII bù tỷ lệ khung hình font chữ (Aspect Ratio Correction)
2. Grayscale ITU-R BT.601
3. Lanczos resampling
4. Trích xuất mảng 2 chiều ma trận điểm ảnh (Pixel Matrix)
"""

from pathlib import Path
from typing import Union, Tuple, List
from PIL import Image


def calculate_ascii_dimensions(
    orig_width: int,
    orig_height: int,
    target_width: int = 100,
    aspect_ratio_correction: float = 0.55
) -> Tuple[int, int]:
    """
    Tính toán kích thước mới cho ảnh ASCII.

    RATIO CORRECTION:
    ------------------------------------------------
    - Pixel là hình vuông có tỉ lệ W:H = 1:1.
    - Các ký tự của Monospace font trong terminal là hình chữ nhật đứng: W/H ≈ 0.5 - 0.55
    - Nên phải nhân chiều cao với aspect_ratio_correction ≈ 0.55

    tỷ_lệ_gốc = orig_height / orig_width
    new_height = round(target_width * tỷ_lệ_gốc * aspect_ratio_correction)

    Args:
        orig_width (int): width ảnh gốc (pixel)
        orig_height (int): height cao ảnh gốc (pixel)
        target_width (int): Chiều rộng mong muốn ảnh ASCII (số ký tự trên một dòng)
        aspect_ratio_correction (float): Hệ số bù tỷ lệ font monospace (default 0.55)

    Returns:
        Tuple[int, int]: Cặp giá trị (new_width, new_height) theo đơn vị số ký tự
    """
    if orig_width <= 0 or orig_height <= 0:
        raise ValueError(f"Kích thước ảnh không hợp lệ: {orig_width}x{orig_height}")
    
    if target_width <= 0:
        raise ValueError(f"Target width phải lớn hơn 0, nhận được: {target_width}")

    # Tính tỷ lệ co giãn dựa
    aspect_ratio = orig_height / orig_width
    new_height = int(round(target_width * aspect_ratio * aspect_ratio_correction))

    new_height = max(1, new_height)

    return target_width, new_height


def load_and_preprocess_image(
    image_source: Union[str, Path, Image.Image],
    target_width: int = 100,
    aspect_ratio_correction: float = 0.55,
    to_grayscale: bool = True
) -> Image.Image:
    """
    Đọc ảnh, chuyển hệ màu xám (nếu cần), co giãn kích thước ảnh

    GRAY SCALE (ITU-R BT.601):
        Độ sáng Y = 0.299 * R + 0.587 * G + 0.114 * B
    - Kết quả: Mỗi pixel RGB trở thành 1 kênh duy nhất từ 0 (đen) đến 255 (trắng)

    LANCZOS RESAMPLING
    ------------------------------------------------
    - Khi co nhỏ ảnh (Downsampling) từ độ phân giải cao xuống cỡ nhỏ (100 ký tự),
      nếu dùng Nearest Neighbor ảnh sẽ bị vỡ răng cưa
    - Bộ lọc Lanczos sử dụng windowed sinc filter qua 8 điểm láng giềng,
      giúp bảo toàn tối đa các chi tiết viền nét sắc mảnh của ảnh gốc trước khi đưa vào phát hiện biên Sobel

    Args:
        image_source (Union[str, Path, Image.Image]): Đường dẫn tới file ảnh hoặc đối tượng PIL Image
        target_width (int): Chiều rộng ký tự
        aspect_ratio_correction (float): Hệ số bù tỷ lệ (default 0.55)
        to_grayscale (bool): Có chuyển sang ảnh xám 8-bit (mode 'L') hay không
        L = Luminance = 0.299 * R + 0.587 * G + 0.114 * B

    Returns:
        Image.Image: Đối tượng PIL Image đã được resize và chuyển hệ màu
    """
    if isinstance(image_source, (str, Path)):
        img_path = Path(image_source)
        if not img_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file ảnh tại đường dẫn: {img_path}")
        image = Image.open(img_path)
    elif isinstance(image_source, Image.Image):
        image = image_source
    else:
        raise TypeError(f"image_source phải là đường dẫn hoặc PIL.Image, nhận được: {type(image_source)}")

    # Bước 1: Chuyển đổi không gian màu sang Grayscale (mode 'L')
    if to_grayscale and image.mode != 'L':
        image = image.convert('L')

    # Bước 2: Tính toán kích thước mới bù tỷ lệ font
    orig_w, orig_h = image.size
    new_w, new_h = calculate_ascii_dimensions(
        orig_width=orig_w,
        orig_height=orig_h,
        target_width=target_width,
        aspect_ratio_correction=aspect_ratio_correction
    )

    # Bước 3: Resize ảnh với bộ lọc nội suy chất lượng cao Lanczos
    # Lưu ý: Pillow >= 9.1.0 khuyến nghị dùng Resampling.LANCZOS
    resampling_filter = getattr(Image, "Resampling", Image).LANCZOS
    resized_image = image.resize((new_w, new_h), resample=resampling_filter)

    return resized_image


def get_pixel_matrix(image: Image.Image) -> List[List[int]]:
    """
    Trích xuất ma trận điểm ảnh 2 chiều từ ảnh xám PIL Image

    Args:
        image (Image.Image): Ảnh xám (mode 'L') đã được resize

    Returns:
        List[List[int]]: Ma trận điểm ảnh 2 chiều kích thước [height][width]
    """
    if image.mode != 'L':
        image = image.convert('L')

    width, height = image.size
    # Lấy danh sách pixel dạng phẳng 1D:
    # Trên Pillow mới (>=11.0), get_flattened_data() được khuyến nghị thay cho getdata()
    if hasattr(image, "get_flattened_data"):
        raw_pixels = list(image.get_flattened_data())
    else:
        raw_pixels = list(image.getdata())

    # Cắt mảng phẳng 1D thành ma trận 2D [height][width]
    matrix: List[List[int]] = []
    for y in range(height):
        start_idx = y * width
        row = raw_pixels[start_idx : start_idx + width]
        matrix.append(row)

    return matrix
