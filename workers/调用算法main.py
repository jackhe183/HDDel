import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
# 保留算法导入，根据需要启用
# from 最大裂谷算法 import find_slip_starts
# from 簇过滤算法 import find_slip_starts
# from 均衡分割算法 import find_slip_starts   # 全对了
# from 自适应分割算法 import find_slip_starts  # 全对了
# from 聚类拟合算法 import find_slip_starts  # 全对了
# from 高级分割算法 import find_slip_starts # 全错了
# from 智能决策算法 import find_slip_starts # 自动大部分错，强制联数=2全部正确
# from 稳健间距算法 import find_slip_starts # 自动大部分错，强制联数=2全部正确
# from 奥卡姆剃刀算法 import find_slip_starts # 自动大部分错，强制联数=2全部正确
# from 结构匹配算法 import find_slip_starts  # 全对了

from .结构匹配算法 import find_slip_starts

def compare_results(raw_result: List[int], gt_result: List[int] | None) -> Dict[str, Any]:
    """
    比较算法结果(raw)和标准答案(GT)，忽略GT的首尾元素。

    Args:
        raw_result: 算法计算出的结果列表。
        gt_result: 从GT文件加载的标准答案列表，如果不存在则为None。

    Returns:
        一个包含 raw, GT, 和 Val 的字典。
    """
    if gt_result is None:
        return {"raw": raw_result, "GT": "Not Found", "Val": False}
    if len(gt_result) < 3:
        return {"raw": raw_result, "GT": gt_result, "Val": False}

    gt_for_comparison = gt_result[1:-1]
    if len(raw_result) != len(gt_for_comparison):
        validation = False
    else:
        validation = [raw == gt for raw, gt in zip(raw_result, gt_for_comparison)]

    return {
        "raw": raw_result,
        "GT": gt_result,
        "Val": validation
    }


def process_and_compare(
        input_json_path: str,
        gt_json_path: str,
        expected_slips: int,
        output_folder_path: Optional[str] = None  # 改为可选文件夹路径，默认None
) -> Dict[str, Dict[str, Any]]:
    """
    核心处理函数：读取JSON文件，调用算法，与GT比较，并按需保存结果。

    Args:
        input_json_path: 输入的坐标信息JSON文件路径
        gt_json_path: 标准答案(Ground Truth)JSON文件路径
        expected_slips: 期望分割出的回单联数
        output_folder_path: 结果JSON文件的保存文件夹路径（可选）
                           - 填写路径：在该文件夹下生成结果文件
                           - 不填（默认None）：不生成文件，仅将结果存入变量并打印

    Returns:
        结构化的比较结果字典（key为文件名，value为包含raw/GT/Val的字典）
    """
    # --- 1. 路径初始化 ---
    input_path = Path(input_json_path)
    # 生成结果文件名（沿用原规则：输入文件名+_comparison_results）
    output_filename = f"{input_path.stem}_comparison_results.json"
    # 若指定了保存文件夹，拼接完整输出路径
    full_output_path = Path(output_folder_path) / output_filename if output_folder_path else None

    # --- 2. 读取输入文件 ---
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        print(f"成功读取输入文件: {input_path}")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"错误：无法读取输入文件 {input_path}。原因: {e}")
        return {}

    # --- 3. 读取GT文件 ---
    try:
        with open(gt_json_path, 'r', encoding='utf-8') as f:
            gt_data = json.load(f)
        print(f"成功读取GT文件: {gt_json_path}")
    except FileNotFoundError:
        print(f"警告：GT文件不存在 -> {gt_json_path}。将无法进行比较。")
        gt_data = {}
    except json.JSONDecodeError as e:
        print(f"错误：GT文件 {gt_json_path} 格式无效。原因: {e}")
        return {}

    # --- 4. 核心算法计算与结果比较 ---
    comparison_results = {}  # 存储最终结果的变量
    run_mode = f"自动判断模式" if expected_slips <= 0 else f"强制 {expected_slips} 联模式"
    print(f"\n--- 开始处理 ({run_mode}) ---")

    for filename, data_list in input_data.items():
        raw_result = find_slip_starts(data_list, expected_slips)
        gt_result = gt_data.get(filename)
        comparison_results[filename] = compare_results(raw_result, gt_result)
        print(f"  > 已处理并比较: {filename}")

    # --- 5. 结果打印与按需保存 ---
    print("\n--- 处理与比较结果 ---")
    # 格式化打印结果（便于阅读）
    formatted_results = json.dumps(comparison_results, indent=4, ensure_ascii=False)
    print(formatted_results)

    # 若指定了保存文件夹，生成结果文件
    if full_output_path:
        try:
            # 确保保存文件夹存在（不存在则创建）
            full_output_path.parent.mkdir(parents=True, exist_ok=True)
            # 写入文件
            with open(full_output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_results)
            print(f"\n结果已保存至: {full_output_path.resolve()}")
        except IOError as e:
            print(f"\n错误：无法写入结果文件 -> {full_output_path}。原因: {e}")

    # 返回结构化结果（方便后续代码复用该结果）
    return comparison_results


def main():
    """主入口函数，设置默认配置并调用核心处理函数"""
    # ==================== 用户配置区 ====================
    # 1. 输入的坐标信息JSON文件路径
    INPUT_JSON_PATH = '../data/image_info.json'
    # 2. 标准答案(Ground Truth)JSON文件路径
    GT_JSON_PATH = '../data/image_GT.json'
    # 3. 期望分割出的回单联数
    EXPECTED_SLIPS = 2
    # 4. 结果保存文件夹路径（可选）
    #    - 填写示例：r"./回单结果文件夹"（当前目录下创建文件夹）
    #    - 不填：设为None（仅打印结果，不生成文件）
    OUTPUT_FOLDER_PATH = None  # 此处改为具体路径即可保存文件
    # ====================================================

    # 调用核心处理函数（并接收返回的结构化结果）
    final_results = process_and_compare(
        input_json_path=INPUT_JSON_PATH,
        gt_json_path=GT_JSON_PATH,
        expected_slips=EXPECTED_SLIPS,
        output_folder_path=OUTPUT_FOLDER_PATH
    )

    # （可选）后续可直接使用 final_results 变量做进一步处理
    # 示例：print(f"\n后续处理：共处理 {len(final_results)} 个文件")


if __name__ == "__main__":
    main()