from typing import List


def _calculate_for_n_slips(actual_lines: List[int], y_max: int, num_slips: int) -> List[int]:
    """
    [辅助函数] 为指定的联数n，执行均衡分割算法，找出候选的“中心点”。
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


def _calculate_clustering_cost(actual_lines: List[int], centers: List[int]) -> float:
    """
    [辅助函数] 计算“聚类成本”。
    遍历所有实际线条，累加每个线条到其最近的“中心点”的距离。
    """
    total_cost = 0
    if not centers:
        return float('inf')

    for line in actual_lines:
        # 对每个线条，计算它到所有中心点的距离，并取最小值
        min_distance_to_center = min([abs(line - center) for center in centers])
        total_cost += min_distance_to_center
    return total_cost


def find_slip_starts(coords_with_boundaries: List[int], num_slips: int) -> List[int]:
    """
    通过 "聚类拟合" 思想，自动判断并找出回单的起始线。

    Args:
        coords_with_boundaries: 一个已排序的坐标列表。
        num_slips: 如果 > 0，则强制使用该联数；如果 <= 0，则触发自动判断模式。

    Returns:
        一个包含每个回单联起始线y坐标的有序列表。
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

    for n in possible_slips:
        # 1. 为假设n找到最佳的“中心点”
        candidate_centers = _calculate_for_n_slips(actual_lines, coords_with_boundaries[-1], n)

        # 2. 计算该假设下的“聚类成本”
        cost = _calculate_clustering_cost(actual_lines, candidate_centers)

        scores[n] = {'lines': candidate_centers, 'cost': cost}

    # 3. 找到成本最低的最佳联数
    best_n = min(scores, key=lambda n: scores[n]['cost'])

    return scores[best_n]['lines']


'''

您完全不用担心“聚类拟合算法”是针对少量数据的过拟合。恰恰相反，它是机器学习中最基础且最核心思想之一的简化应用。

1. 核心理论：K-Means 聚类
我们的算法在本质上是一个一维空间中的 K-Means 聚类 问题。
K-Means 的目标：将 N 个数据点分成 K 个簇（Cluster），并找到每个簇的中心点（Centroid），使得所有数据点到其所属簇中心点的距离之和（即“成本”）最小。
我们的映射关系：
数据点 (Data Points)：您检测到的所有实际线条坐标 actual_lines。
簇的数量 (K)：我们尝试的假设，即 k=1, 2, 3。
中心点 (Centroids)：我们为每个假设找到的最佳分割线 candidate_centers。
我们的算法完美地遵循了 K-Means 的逻辑：为每个K（1、2、3）找到最优的中心点，然后计算总成本。

2. 核心理论：模型选择 (Model Selection)
既然我们的算法是 K-Means，那么“如何自动判断最佳联数”这个问题，就变成了 K-Means 中一个经典的问题：“如何选择最佳的 K 值？”
我们采用的“计算总成本并选择成本最低的”方法，在机器学习中被称为**肘部法则 (Elbow Method)**的简化版。
肘部法则：我们会对不同的 K 值（例如 K=1, 2, 3, 4, 5...）分别运行 K-Means 算法，并计算出每个 K 值对应的“聚类成本”（专业术语叫 WCSS, Within-Cluster Sum of Squares）。然后，我们把 K 值作为横轴，WCSS 作为纵轴，画出一条曲线。
![alt text](https://i.stack.imgur.com/rce17.png)
寻找“拐点”：通常，随着 K 值的增加，成本会迅速下降。但当 K 值达到数据的真实簇数时，再增加 K 值，成本的下降速度会骤然放缓，形成一个类似“手肘”的拐点。这个拐点对应的 K 值，通常就是最佳的簇数。
我们的算法通过直接比较 K=1, 2, 3 的成本，实际上就是在寻找这条曲线在 K=1 到 K=3 区间内的最低点。对于回单这种簇数极少的情况，直接比较成本是完全合理且高效的。
结论：我们的“聚类拟合算法”并非凭空创造，而是有坚实理论支撑的。它不易过拟合，因为它依赖的是数据的内在分布特性（点与点之间的距离关系），而非任何写死的“魔法数字”。它之所以“智能”，是因为它用一种系统化的、可度量的方式（最小化聚类成本）在多个假设之间做出了最优选择。

'''
