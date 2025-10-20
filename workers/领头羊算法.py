import json


def filter_redundant_data(nums, threshold):
    """
    根据给定的阈值过滤冗余的、位置相近的数据点。

    这个函数实现了“根据邻近度分组”的算法。它遍历一个排序好的列表，
    当发现当前元素与前一个元素的差值大于或等于阈值时，就认为开启了
    一个新的“簇”，并将该元素作为新簇的代表。

    Args:
        nums (list[int]): 一个升序排列的整数列表（代表y坐标）。
        threshold (int): 一个正整数，用于判断是否开启新簇的阈值。

    Returns:
        list[int]: 一个仅包含每个簇代表值的新列表。
    """
    # 如果列表为空，直接返回空列表
    if not nums:
        return []

    # 列表的第一个元素永远是第一个簇的代表
    filtered_list = [nums[0]]

    # 从第二个元素开始遍历，与它紧邻的前一个元素进行比较
    for i in range(1, len(nums)):
        # 计算与前一个点的差值
        gap = nums[i] - nums[i - 1]

        # 如果差值大于或等于阈值，说明这是一个新的簇的开始
        if gap >= threshold:
            filtered_list.append(nums[i])

    return filtered_list


def main():
    """
    主执行函数：读取输入数据，处理并打印结果。
    """
    # 1. 输入数据：使用您提供的所有示例数据
    # 这是输入JSON应有的格式
    input_data = {
        "list_1": [22, 164, 1135, 1283, 2264],
        "list_2": [22, 164, 1134, 1283, 2264],
        "list_3": [15, 96, 153, 561, 655, 711, 1116],
        "list_4": [15, 96, 154, 561, 655, 711, 1116],
        "list_5": [47, 216, 321, 1222, 1383, 1487],
        "list_6": [70, 398, 565, 1060],
        "list_7": [70, 400, 566, 947, 1056]
    }

    # 2. 设定阈值
    # 这个值是判断“距离远近”的标准。根据您的数据，300是一个比较合适的临界值，
    # 能够有效区分开内部紧凑的线条和不同区块之间的巨大间隔。
    THRESHOLD = 300

    # 3. 处理数据
    output_data = {}
    for key, num_list in input_data.items():
        # 调用核心算法函数进行处理
        filtered_result = filter_redundant_data(num_list, THRESHOLD)
        # 将结果存入输出字典
        output_data[f"filtered_{key}"] = filtered_result

    # 4. 打印输入与输出的JSON
    # 使用 indent=4 参数美化JSON输出，使其更易读
    print("--- 输入JSON ---")
    print(json.dumps(input_data, indent=4))

    print("\n--- 输出JSON ---")
    print(json.dumps(output_data, indent=4))


# 当该脚本被直接运行时，执行main函数
if __name__ == "__main__":
    main()