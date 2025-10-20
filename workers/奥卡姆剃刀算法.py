import numpy as np
from typing import List


# ... _run_forced_mode 保持不变 ...
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
    [自动模式] 最终版奥卡姆剃刀算法：
    首先判断是否存在一个“鹤立鸡群”的最大间距，这覆盖了绝大多数二联单的情况。
    如果不存在，再使用更通用的“断层”分析来处理多联或单联。
    """
    if len(actual_lines) <= 1:
        return actual_lines

    gaps = np.diff(actual_lines)
    if len(gaps) < 2:
        return [actual_lines[0]]

    sorted_gaps = np.sort(gaps)[::-1]

    # --- 核心决策逻辑 ---
    max_gap = sorted_gaps[0]
    second_max_gap = sorted_gaps[1]

    # 定义一个“显著”的比率阈值
    SIGNIFICANT_RATIO = 2.0

    # 场景1：存在一个“鹤立鸡群”的唯一最大间距（最常见的情况）
    if max_gap / (second_max_gap + 1e-9) > SIGNIFICANT_RATIO:
        num_splits = 1
    # 场景2：不存在唯一王者，需要寻找“断层”来确定有几个分割点
    else:
        ratios = sorted_gaps[:-1] / (sorted_gaps[1:] + 1e-9)
        # 如果连断层都不显著，那就是单联
        if np.max(ratios) < SIGNIFICANT_RATIO:
            num_splits = 0
        else:
            # 分割点的数量 = 断层的位置 + 1
            num_splits = np.argmax(ratios) + 1

    # --- 根据决策结果，找出分割线 ---
    if num_splits == 0:
        return [actual_lines[0]]

    # 分割阈值是第 num_splits 个最大间距
    threshold = sorted_gaps[num_splits - 1]

    # 找出所有大于等于阈值的间距，它们就是分割点
    # 用 ">=" 是为了处理多个间距相等的情况
    break_indices = np.where(gaps >= threshold)[0]
    start_lines = [actual_lines[i + 1] for i in break_indices]

    final_result = sorted(list(set([actual_lines[0]] + start_lines)))
    return final_result


def find_slip_starts(coords_with_boundaries: List[int], num_slips: int) -> List[int]:
    actual_lines = coords_with_boundaries[1:-1]
    if not actual_lines:
        return []

    if num_slips > 0:
        return _run_forced_mode(actual_lines, coords_with_boundaries[-1], num_slips)
    else:
        return _run_auto_mode(actual_lines)