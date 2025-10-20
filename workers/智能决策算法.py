import numpy as np
from typing import List


def _calculate_for_n_slips(actual_lines: List[int], y_max: int, num_slips: int) -> List[int]:
    """
    [辅助函数] 为指定的联数n，执行均衡分割算法，找出候选的“中心点”。
    (此函数与“聚类拟合算法”中的完全相同)
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


def _calculate_bic(actual_lines: List[int], centers: List[int]) -> float:
    """
    [核心决策函数] 计算给定模型的贝叶斯信息准则 (BIC) 分数。
    BIC = n * log(RSS/n) + k * log(n)
    分数越低，模型越好。
    """
    n = len(actual_lines)  # n: 数据点数量
    k = len(centers)  # k: 模型参数数量 (即联数/中心点数)

    if n == 0 or k == 0:
        return float('inf')

    # 1. 计算残差平方和 (RSS)
    rss = 0
    for line in actual_lines:
        min_distance = min([abs(line - center) for center in centers])
        rss += min_distance ** 2

    # 2. 计算 BIC
    # 为了避免 log(0) 的数学错误，如果 rss 为 0，给它一个极小值。
    if rss == 0:
        rss = 1e-9

    bic_score = n * np.log(rss / n) + k * np.log(n)

    return bic_score


def find_slip_starts(coords_with_boundaries: List[int], num_slips: int) -> List[int]:
    """
    通过 "BIC模型选择" 与 "均衡分割" 结合，智能判断并找出回单的起始线。
    这是迄今最稳健、理论最扎实的版本。
    """
    actual_lines = coords_with_boundaries[1:-1]
    if not actual_lines:
        return []

    # 强制模式：直接调用均衡分割算法
    if num_slips in [1, 2, 3]:
        return _calculate_for_n_slips(actual_lines, coords_with_boundaries[-1], num_slips)

    # --- 自动判断模式 ---
    scores = {}
    possible_slips = [1, 2, 3]

    for k in possible_slips:
        # 1. 为假设k找到最佳的“中心点”
        candidate_centers = _calculate_for_n_slips(actual_lines, coords_with_boundaries[-1], k)

        # 2. 计算该假设的 BIC 分数
        bic_score = _calculate_bic(actual_lines, candidate_centers)

        scores[k] = {'lines': candidate_centers, 'bic': bic_score}

    # 3. 找到 BIC 分数最低的最佳联数
    best_k = min(scores, key=lambda k: scores[k]['bic'])

    return scores[best_k]['lines']


'''

核心思想：一个好的模型，不仅要“拟合得好”（误差小），还要“足够简单”（复杂度低）。我们必须在两者之间找到一个平衡点。
在统计学中，解决这个问题的标准工具是信息准则 (Information Criterion)，最常用的就是 BIC (贝叶斯信息准则)。
BIC 的直观解释：
BIC分数 = 数据拟合度(误差) + 模型复杂度惩罚
数据拟合度：数据点离它所属的中心点有多远。我们用残差平方和 (RSS) 来衡量，这比简单的距离求和更标准。
模型复杂度惩罚：模型用了多少个参数（在这里就是联数 K）。联数越多，惩罚就越重。
算法会计算 K=1, 2, 3 时各自的 BIC 分数，然后选择分数最低的那个。这次，1联不会因为误差是0就胜出，2联或3联也不会因为中心点多就占便宜。只有当增加一个中心点带来的误差下降足够大，能够抵消掉复杂度惩罚的增加时，更复杂的模型才会被选中。
这才是真正“智能”的决策。

'''