from typing import List, Dict, Any


def find_slip_starts(coords_with_boundaries: List[int], num_slips: int) -> List[int]:
    """
    通过 "自适应分割" 思想，自动判断并找出回单的起始线。

    算法核心思想:
    1. 预先假设图片可能为 1, 2, 或 3 联。
    2. 对每一种假设，使用 "均衡分割" 逻辑计算出候选的起始线集合。
    3. 同时，计算每一种假设的 "拟合误差"——即找出的实际线条与理论位置的平均偏差。
    4. 比较三种假设的拟合误差，选择误差最小的那一种作为最佳模型。
    5. 返回最佳模型对应的起始线集合。

    Args:
        coords_with_boundaries: 一个已排序的坐标列表。
        num_slips: (可选) 如果提供一个大于0的值 (如1, 2, 3)，则强制使用该联数进行计算。
                   如果值为0或-1，则触发自动判断模式。

    Returns:
        一个包含每个回单联起始线y坐标的有序列表。
    """
    actual_lines = coords_with_boundaries[1:-1]

    if not actual_lines:
        return []

    # 如果用户强制指定了联数，则直接使用均衡分割算法计算
    if num_slips in [1, 2, 3]:
        return _calculate_for_n_slips(actual_lines, coords_with_boundaries[-1], num_slips)

    # --- 自动判断模式 ---
    possible_slips = [1, 2, 3]
    scores: Dict[int, Dict[str, Any]] = {}

    for n in possible_slips:
        # 1. 为当前假设（n联）计算候选分割线
        candidate_lines = _calculate_for_n_slips(actual_lines, coords_with_boundaries[-1], n)

        # 2. 计算该假设下的理论位置和总误差
        anchor_point = actual_lines[0]
        total_height = coords_with_boundaries[-1] - anchor_point
        average_height = total_height / n

        total_error = 0
        for line in candidate_lines:
            # 找到这个line是哪个理想位置的最佳匹配
            # (line - anchor_point) / average_height 会得到一个接近整数的索引
            closest_ideal_index = round((line - anchor_point) / average_height)
            ideal_position = anchor_point + closest_ideal_index * average_height
            total_error += abs(line - ideal_position)

        # 3. 计算平均误差作为最终得分（分数越小越好）
        # 加一个极小值避免除以零
        average_error = total_error / n
        scores[n] = {'lines': candidate_lines, 'error': average_error}

    # 4. 找到误差最小的最佳联数
    # min函数的key参数是用来比较的依据，这里我们用字典里的'error'值
    best_n = min(scores, key=lambda n: scores[n]['error'])

    return scores[best_n]['lines']


def _calculate_for_n_slips(actual_lines: List[int], y_max: int, num_slips: int) -> List[int]:
    """
    为指定的联数n，执行均衡分割算法。
    """
    if not actual_lines or num_slips <= 0:
        return []
    if num_slips == 1:
        return [actual_lines[0]]

    anchor_point = actual_lines[0]
    total_height = y_max - anchor_point
    average_height = total_height / num_slips

    slip_starts = {anchor_point}

    for i in range(1, num_slips):
        ideal_position = anchor_point + i * average_height
        closest_line = min(actual_lines, key=lambda line: abs(line - ideal_position))
        slip_starts.add(closest_line)

    return sorted(list(slip_starts))