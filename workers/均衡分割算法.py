from typing import List


def find_slip_starts(coords_with_boundaries: List[int], num_slips: int) -> List[int]:
    """
    通过 "均衡分割" 思想，在一个坐标列表中找出各联回单的起始线。

    算法核心思想:
    1. 假设一张包含 N 联回单的图片，其总高度被大致均分成了 N 份。
    2. 计算出每一联的平均高度。
    3. 根据平均高度，推算出每一联理想的、理论上的起始y坐标。
    4. 在实际检测到的线条中，寻找与这个理想坐标最接近的那个点，作为该联的实际起始点。

    这个算法具有全局视角，鲁棒性远超前两个版本。

    Args:
        coords_with_boundaries: 一个已排序的坐标列表，
                                必须以 0 开始，以图片高度 ymax 结束。
        num_slips: 期望分割出的回单联数。

    Returns:
        一个包含每个回单联起始线y坐标的有序列表。
    """
    # 1. 提取出实际的线条坐标（排除列表头尾的 0 和 ymax）
    actual_lines = coords_with_boundaries[1:-1]

    # 2. 处理边界情况
    if not actual_lines or num_slips <= 0:
        return []
    if num_slips == 1:
        return [actual_lines[0]]

    # 3. 核心逻辑：计算理想分割点并寻找最近的实际线条

    # 3.1 确定分割的基准点和总高度。我们以第一条实际线为基准，更稳定。
    anchor_point = actual_lines[0]
    total_height = coords_with_boundaries[-1] - anchor_point
    average_height = total_height / num_slips

    slip_starts = {anchor_point}  # 使用集合以自动处理重复

    # 3.2 循环查找第 2 到第 N 联的起始点
    for i in range(1, num_slips):
        # 计算理论上第 i+1 联的起始坐标
        ideal_position = anchor_point + i * average_height

        # 在所有实际线条中，找到距离这个理论值最近的一个
        # min() 的 key 参数是一个 lambda 函数，它为每个 line 计算与 ideal_position 的差的绝对值
        # min() 会返回那个使得这个绝对值最小的 line
        closest_line = min(actual_lines, key=lambda line: abs(line - ideal_position))
        slip_starts.add(closest_line)

    # 4. 返回排序后的结果列表
    return sorted(list(slip_starts))