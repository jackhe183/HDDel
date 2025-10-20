import numpy as np
import ruptures as rpt
from typing import List


def find_slip_starts(coords_with_boundaries: List[int], num_slips: int) -> List[int]:
    """
    使用 "变化点检测" 算法，自动识别并找出回单的起始线。

    该方法将线条坐标的 "间距" 视为一个信号序列，并寻找该信号发生剧烈变化的点，
    这些点即对应回单联的分割处。这是解决此类问题的专业且优雅的方案。

    Args:
        coords_with_boundaries: 一个已排序的坐标列表。
        num_slips: 在此算法中，此参数被用作一个参考上限。
                   如果<=0, 则由算法自由寻找最佳分割点（最多3个）。
                   如果>0, 则算法最多寻找 num_slips-1 个分割点。

    Returns:
        一个包含每个回单联起始线y坐标的有序列表。
    """
    actual_lines = coords_with_boundaries[1:-1]
    if not actual_lines:
        return []

    # 如果只有一条或两条线，无法形成有意义的间距信号
    if len(actual_lines) <= 2:
        return [actual_lines[0]]

    # 1. 将“坐标”转换为“间距”信号
    # np.diff() 会计算相邻元素的差值，这正是我们关心的“间距”
    gaps = np.diff(actual_lines)

    # 2. 初始化变化点检测算法 (PELT)
    # model="rbf": 使用径向基函数模型，对均值变化（即间距大小变化）很敏感。
    # min_size=1: 允许的最小段落长度为1。
    # jump=1: 每次跳跃1个数据点进行搜索，保证精度。
    algo = rpt.Pelt(model="rbf", min_size=1, jump=1)

    # 3. 传入信号并进行拟合
    # pen: 惩罚值。值越大，找到的变化点越少。
    #      我们可以通过尝试1,2,3联的总线数来动态寻找一个合理的惩罚值，
    #      但通常一个基于数据标准差的经验值效果很好。
    #      这里我们用一个更简单的方法：直接限定最多找几个点。
    algo.fit(gaps)

    # 4. 预测变化点
    # 我们知道联数最多3联，即分割点最多2个。
    # 如果用户指定了联数，我们也遵从那个上限。
    max_breaks = (num_slips - 1) if num_slips > 1 else 2

    try:
        # predict方法可以接受一个目标数量 n_bkps
        result_indices = algo.predict(n_bkps=max_breaks)
    except Exception:
        # 如果数据太少或分布极端，可能找不到那么多分割点，这里做个保护
        # 使用 pen (惩罚项) 进行预测，通常更稳健
        penalty = np.log(len(gaps)) * np.std(gaps) ** 2  # 经验惩罚值
        result_indices = algo.predict(pen=penalty)

    # result_indices 返回的是分割点在 gaps 数组中的索引。
    # 例如，[180] 意味着在 gaps[180] 之后发生了变化。
    # 这对应于 actual_lines[180] 和 actual_lines[181] 之间。
    # 所以，新的回单联是从 actual_lines[181] 开始的。
    # 最后一个索引是数组长度，需要去掉。
    break_points_in_gaps = [idx for idx in result_indices if idx < len(gaps)]

    # 将间距索引转换为实际的线条坐标
    start_line_coords = [actual_lines[i] for i in break_points_in_gaps]

    # 5. 最终结果总是包含第一条线
    final_starts = sorted(list(set([actual_lines[0]] + start_line_coords)))

    return final_starts