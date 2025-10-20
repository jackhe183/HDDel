import os
import cv2
import numpy as np
import json
import glob

def extract_image_data(image_path):
    """
    从单个图片文件中提取绿色线条的Y坐标和图片的总高度。

    该函数会处理中文路径，并在内部完成所有必要的图像处理。

    Args:
        image_path (str): 图片的完整文件路径。

    Returns:
        tuple: 一个包含 (y_positions, height) 的元组。
               - y_positions (list[int]): 检测到的所有绿色线条的Y坐标列表。
               - height (int): 图片的总高度。
               如果图片无法读取，则返回 (None, None)。
    """
    # 使用 imdecode 来正确处理包含非ASCII字符（如中文）的路径
    try:
        image_data = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image_data is None:
            raise IOError("解码后的图像数据为空")
    except Exception as e:
        print(f"警告：无法读取或解码图片 '{os.path.basename(image_path)}'，原因: {e}。已跳过。")
        return None, None

    # 获取图片总高度（image.shape -> (高度, 宽度, 通道数)）
    height = image_data.shape[0]

    # 提取绿色线条的Y坐标
    hsv_image = cv2.cvtColor(image_data, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv_image, lower_green, upper_green)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    y_positions = []
    if contours:
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            y_positions.append(y)

    return y_positions, height


def get_images_lines_info(source_folder_path: str, output_folder_path: str):
    """
    主执行函数：遍历图片文件夹，处理数据，并在输出文件夹生成JSON结果。

    Args:
        source_folder_path (str): 存放图片的文件夹路径。
        output_folder_path (str): 输出JSON文件所在的**文件夹路径**（JSON文件会被命名为 `image_info.json`）。
    """
    # 检查源文件夹是否存在
    if not os.path.isdir(source_folder_path):
        print(f"错误：输入文件夹 '{source_folder_path}' 不存在或不是有效目录。")
        return

    print(f">>> 开始处理文件夹: {source_folder_path}")

    # 查找所有支持的图片格式（可根据需要扩展，如 .png、.bmp）
    supported_formats = ["*.jpg", "*.jpeg"]
    image_paths = []
    for fmt in supported_formats:
        image_paths.extend(glob.glob(os.path.join(source_folder_path, fmt)))

    if not image_paths:
        print("警告：指定文件夹中未找到任何支持的图片文件。")
        return

    final_results = {}  # 存储所有图片的处理结果

    # 遍历每张图片
    for img_path in image_paths:
        filename = os.path.basename(img_path)
        print(f"--- 正在处理: {filename} ---")

        y_coords, img_height = extract_image_data(img_path)
        if y_coords is None or img_height is None:
            continue  # 跳过处理失败的图片

        # 构建最终数据结构：[0, y1, y2, ..., 图片总高度]
        final_data = [0] + y_coords + [img_height]
        final_results[filename] = final_data

    if not final_results:
        print("\n处理结束，但未成功处理任何图片。")
        return

    # 拼接输出JSON的完整路径（在输出文件夹下生成 image_info.json）
    output_json_path = os.path.join(output_folder_path, "image_info.json")
    try:
        # 确保输出文件夹存在（若不存在则创建）
        os.makedirs(output_folder_path, exist_ok=True)
        # 写入JSON文件
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=4, ensure_ascii=False)
        print(f"\n处理完成！结果已保存至: {os.path.abspath(output_json_path)}")
    except IOError as e:
        print(f"\n错误：无法写入JSON文件。原因: {e}")


# 脚本主入口
if __name__ == "__main__":
    # 示例调用：替换为真实路径
    source_path = r"/申元回单切割/拆点功能1017/新建文件夹"  # 图片所在文件夹
    output_folder = "../data"  # 输出JSON的文件夹（会生成 ../data/image_info.json）
    get_images_lines_info(source_path, output_folder)