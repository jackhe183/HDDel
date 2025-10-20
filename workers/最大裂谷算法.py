import json
from pathlib import Path
from typing import List, Dict, Any


def find_slip_starts(coords_with_boundaries: List[int], num_slips: int) -> List[int]:
    """
    在一个已包含边界（0和ymax）的坐标列表中，找出各联回单的起始线。

    此函数是算法的核心，它优雅、高效且不包含任何数据猜测逻辑。
    它通过寻找坐标之间最大的 N-1 个间距（“裂谷”）来确定分割点。

    Args:
        coords_with_boundaries: 一个已排序的坐标列表，
                                必须以 0 开始，以图片高度 ymax 结束。
        num_slips: 期望分割出的回单联数。

    Returns:
        一个包含每个回单联起始线y坐标的有序列表。
    """
    # 1. 提取出实际的线条坐标（排除列表头尾的 0 和 ymax）
    actual_lines = coords_with_boundaries[1:-1]

    # 2. 处理边界情况：如果无需分割或数据不足，则返回第一条线
    if not actual_lines:
        return []
    if num_slips <= 1:
        return [actual_lines[0]]

    # 3. 核心逻辑：计算所有间距，并与间距后的坐标配对
    gaps = [
        (coords_with_boundaries[i] - coords_with_boundaries[i - 1], coords_with_boundaries[i])
        for i in range(1, len(coords_with_boundaries))
    ]

    # 4. 排序并筛选出最大的 N-1 个“裂谷”作为分割点
    gaps.sort(key=lambda x: x[0], reverse=True)
    num_dividers = num_slips - 1
    divider_coords = [coord for gap, coord in gaps[:num_dividers]]

    # 5. 组合最终结果：第一条线 + 所有分割点，并排序
    start_lines = sorted(list(set([actual_lines[0]] + divider_coords)))

    return start_lines


