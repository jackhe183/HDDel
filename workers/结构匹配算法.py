from typing import List, Tuple, Optional


def _calculate_match_score(actual_lines: List[int], y_max: int, num_slips: int) -> Tuple[float, List[int]]:
    """
    计算特定联数假设下的“匹配得分”和对应的分割线。
    得分越低表示匹配越好（得分本质是平均相对偏差）。
    """
    if num_slips <= 1:
        return 0.0, [actual_lines[0]]

    anchor = actual_lines[0]
    total_height = y_max - anchor
    average_height = total_height / num_slips

    matched_lines = {anchor}
    total_error_ratio = 0.0

    for i in range(1, num_slips):
        ideal_pos = anchor + i * average_height
        # 找到离理想位置最近的实际线条
        closest_line = min(actual_lines, key=lambda line: abs(line - ideal_pos))
        matched_lines.add(closest_line)

        # 计算相对偏差：距离 / 总高度
        error_ratio = abs(closest_line - ideal_pos) / total_height
        total_error_ratio += error_ratio

    # 平均偏差作为得分
    average_score = total_error_ratio / (num_slips - 1)
    return average_score, sorted(list(matched_lines))


def find_slip_starts(coords_with_boundaries: List[int], num_slips: int) -> List[int]:
    """
    基于 "结构匹配" 的终极算法。
    它利用了 "回单通常是均分的" 这一强先验知识，具有极高的稳健性。
    """
    actual_lines = coords_with_boundaries[1:-1]
    if not actual_lines:
        return []

    # --- 强制模式 ---
    if num_slips > 0:
        _, lines = _calculate_match_score(actual_lines, coords_with_boundaries[-1], num_slips)
        return lines

    # --- 自动模式 ---
    # 核心逻辑：优先检查是否符合2联或3联的“标准结构”。
    # 如果某个假设的平均偏差小于 5% (0.05)，我们就认为找到了正确答案。

    MATCH_THRESHOLD = 0.05  # 5% 的容错率，非常稳健

    # 1. 测试 2 联假设 (最常见情况)
    score_2, lines_2 = _calculate_match_score(actual_lines, coords_with_boundaries[-1], 2)
    if score_2 < MATCH_THRESHOLD:
        return lines_2

    # 2. 测试 3 联假设
    score_3, lines_3 = _calculate_match_score(actual_lines, coords_with_boundaries[-1], 3)
    if score_3 < MATCH_THRESHOLD:
        return lines_3

    # 3. 如果都不符合标准结构，则认为是单联
    return [actual_lines[0]]