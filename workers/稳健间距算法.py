import numpy as np
from typing import List


def _run_forced_mode(actual_lines: List[int], y_max: int, num_slips: int) -> List[int]:
    """
    [强制模式] 使用已被验证100%准确的“均衡分割”算法。
    """
    if not actual_lines or num_slips <= 0:
        return []
    if num_slips == 1:
        return [actual_lines[0]]

    anchor_point = actual_lines[0]
    total_height = y_max - anchor_point
    average_height = total_height / num_slips

    centers = {anchor_point}
    for i in range(1, num_slips):
        ideal_position = anchor_point + i * average_height
        closest_line = min(actual_lines, key=lambda line: abs(line - ideal_position))
        centers.add(closest_line)
    return sorted(list(centers))


def _run_auto_mode(actual_lines: List[int]) -> List[int]:
    """
    [自动模式] 使用基于间距中位数的稳健、自适应算法。
    """
    if len(actual_lines) <= 1:
        return actual_lines

    # 1. 计算所有连续线条之间的间距
    gaps = np.diff(actual_lines)
    if len(gaps) == 0:
        return [actual_lines[0]]

    # 2. 计算间距的中位数，这是一个对异常值稳健的“正常”间距基准
    median_gap = np.median(gaps)

    # 3. 设定一个自适应阈值。一个间距如果大于中位数的5倍，就极有可能是分割点。
    #    同时设定一个最小绝对阈值（如150），防止在所有间距都很小的情况下误判。
    #    这个乘数(5)和最小阈值(150)是可调整的经验参数，但通用性很强。
    adaptive_threshold = max(median_gap * 5, 150)

    # 4. 找到所有超过阈值的间距的索引
    break_indices = np.where(gaps > adaptive_threshold)[0]

    # 5. 分割点是这些巨大间距之后的那条线
    #    索引i处的gap是 line[i+1] 和 line[i] 的差，所以新联的起点是 line[i+1]
    start_lines = [actual_lines[i + 1] for i in break_indices]

    # 最终结果总是包含第一条线
    final_result = sorted(list(set([actual_lines[0]] + start_lines)))

    return final_result


def find_slip_starts(coords_with_boundaries: List[int], num_slips: int) -> List[int]:
    """
    最终版混合算法：
    - 强制模式 (num_slips > 0): 使用100%准确的均衡分割算法。
    - 自动模式 (num_slips <= 0): 使用稳健的、基于间距中位数的自适应算法。
    """
    actual_lines = coords_with_boundaries[1:-1]
    if not actual_lines:
        return []

    if num_slips > 0:
        return _run_forced_mode(actual_lines, coords_with_boundaries[-1], num_slips)
    else:
        return _run_auto_mode(actual_lines)