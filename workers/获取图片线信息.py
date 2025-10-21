import os
import cv2
import numpy as np
import json
import glob


def extract_image_data(image_path):
    """
    【严格按照您的要求】
    先裁剪图片最左侧的极窄区域，然后仅在该区域内检测绿色线条的Y坐标。

    Args:
        image_path (str): 图片的完整文件路径。

    Returns:
        tuple: 一个包含 (y_positions, height) 的元组。
               - y_positions (list[int]): 检测到的绿色线条的Y坐标列表。
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

    # 获取图片总高度和宽度
    height, width = image_data.shape[:2]

    # --- 核心步骤：裁剪图片最左侧的极窄区域 ---
    # 定义要裁剪的宽度，10个像素足以避开所有文字干扰
    CROP_WIDTH = 10
    # 防止图片本身过窄
    if width < CROP_WIDTH:
        left_strip = image_data
    else:
        # 裁剪操作：只取从第0列到第CROP_WIDTH列的像素
        left_strip = image_data[:, 0:CROP_WIDTH]

    # --- 在裁剪后的窄条上，执行最原始的绿色检测 ---
    hsv_image = cv2.cvtColor(left_strip, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv_image, lower_green, upper_green)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    y_positions = []
    if contours:
        for contour in contours:
            # 获取每个绿色区域的Y坐标
            x, y, w, h = cv2.boundingRect(contour)
            y_positions.append(y)

    # --- 清理和合并结果 ---
    # 因为一条粗线可能被识别为多个相邻的Y坐标，需要合并
    if not y_positions:
        return [], height

    # 1. 去重并排序
    y_positions = sorted(list(set(y_positions)))

    # 2. 合并距离非常近的坐标
    merged_y = [y_positions[0]]
    for y in y_positions:
        # 如果当前坐标与上一个已合并坐标的距离大于5像素，才视为一条新线
        if y - merged_y[-1] > 5:
            merged_y.append(y)

    return merged_y, height


def get_images_lines_info(source_folder_path: str, output_folder_path: str):
    """
    主执行函数：遍历图片文件夹，处理数据，并在输出文件夹生成JSON结果。
    """
    if not os.path.isdir(source_folder_path):
        print(f"错误：输入文件夹 '{source_folder_path}' 不存在或不是有效目录。")
        return

    print(f">>> 开始处理文件夹: {source_folder_path}")

    supported_formats = ["*.jpg", "*.jpeg", "*.png"]
    image_paths = []
    for fmt in supported_formats:
        image_paths.extend(glob.glob(os.path.join(source_folder_path, fmt)))

    if not image_paths:
        print("警告：指定文件夹中未找到任何支持的图片文件。")
        return

    final_results = {}
    for img_path in sorted(image_paths):
        filename = os.path.basename(img_path)
        print(f"--- 正在处理: {filename} ---")

        y_coords, img_height = extract_image_data(img_path)
        if y_coords is None or img_height is None:
            continue

        final_data = [0] + y_coords + [img_height]
        final_results[filename] = final_data

    if not final_results:
        print("\n处理结束，但未成功处理任何图片。")
        return

    output_json_path = os.path.join(output_folder_path, "image_info.json")
    try:
        os.makedirs(output_folder_path, exist_ok=True)
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
