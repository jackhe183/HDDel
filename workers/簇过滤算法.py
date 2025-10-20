from typing import List

# --- 算法核心配置 ---
# 这个阈值是新算法的关键。
# 如果一个坐标点与前一个点的距离大于或等于这个值，它就会被视为一个新的回单联的开始。
# 您可以根据实际数据调整此值。根据您提供的示例，400 是一个很好的初始值。
CLUSTERING_THRESHOLD = 400


def _filter_clusters(nums: List[int], threshold: int) -> List[int]:
    """
    根据给定的阈值，对升序排列的数字列表进行聚类，并返回每个簇的代表值。
    这是 "过滤冗余序列数据" 题目的直接实现。
    """
    if not nums:
        return []

    # 1. 列表的第一个数据点自成一派
    representatives = [nums[0]]

    # 2. 从第二个数据点开始遍历
    for i in range(1, len(nums)):
        # 如果当前数据点与上一个数据点的差值大于或等于 threshold
        if nums[i] - nums[i - 1] >= threshold:
            # 开启新簇，当前点成为代表
            representatives.append(nums[i])
        # 否则，差值小于 threshold, 忽略当前点，因为它属于上一个簇

    return representatives


def find_slip_starts(coords_with_boundaries: List[int], num_slips: int) -> List[int]:
    """
    新算法的包装器，保持与旧版 "最大裂谷算法" 相同的接口。

    它使用 "簇过滤算法" 来识别回单联的起始线。

    Args:
        coords_with_boundaries: 一个已排序的坐标列表，
                                必须以 0 开始，以图片高度 ymax 结束。
        num_slips: 期望分割出的回单联数。算法将确保返回的结果不超过这个数量。

    Returns:
        一个包含每个回单联起始线y坐标的有序列表。
    """
    # 1. 提取出实际的线条坐标（排除列表头尾的 0 和 ymax）
    actual_lines = coords_with_boundaries[1:-1]

    # 2. 如果没有实际线条，返回空列表
    if not actual_lines:
        return []

    # 3. 调用核心的簇过滤算法
    # 注意：这里使用了在本文件顶部定义的 CLUSTERING_THRESHOLD
    slip_starts = _filter_clusters(actual_lines, CLUSTERING_THRESHOLD)

    # 4. 确保返回的结果数量不超过预期的联数
    # 这是为了匹配业务需求，例如，即使检测到3个可能的联，如果预期是2，也只返回前2个。
    if num_slips > 0 and len(slip_starts) > num_slips:
        return slip_starts[:num_slips]

    return slip_starts