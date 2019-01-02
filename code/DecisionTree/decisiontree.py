#coding=utf-8
# ==============================================================================
"""使用Python实现决策树
版本：
    Python：3.6.7
参考：
    https://github.com/apachecn/AiLearning
"""
#%%
from math import log
import pickle

from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
import pandas as pd

pd.set_option('precision', 4)

def load_dataset():
    """加载数据集以及特征名称
    Returns:
        train_data: 构造决策树的训练集
        test_data: 用于剪枝和测试的测试集
        features: 数据特征名称
    """
    raw_data = load_wine()
    data = raw_data['data']
    target = raw_data['target']

    print(raw_data['DESCR'])
    features = raw_data['feature_names']
    x_train, x_test, y_train, y_test = train_test_split(
        data, target, test_size=0.2, random_state=2019)

    # 使用Pandas便于计算和处理数据
    train_data = pd.DataFrame(x_train, columns=raw_data['feature_names'])
    test_data = pd.DataFrame(x_test, columns=raw_data['feature_names'])
    # 将label列添加进DataFrame中
    train_data['label'] = y_train
    test_data['label'] = y_test
    # 调用describe获取数据信息
    # train_data.describe()
    return train_data, test_data, features

def cal_ent(dataframe):
    """计算以label为目标的信息熵
    Args:
        dataframe: 数据集DataFrame
    Returns:
        ent_data: 信息熵的值
    """
    ent_data = 0.0
    # value_counts返回label列下的值和对应的出现次数，Series类型
    value_counts = dataframe['label'].value_counts()
    # Series可以使用items()遍历
    for _, value in value_counts.items():
        prob = value / len(dataframe)
        ent_data += - prob * log(prob, 2)
    return ent_data


def split_data(dataframe, feature, threshold):
    """根据阈值划分数据集
    对于连续值的特征，采用插队的方式选出threshold，将数据集划分为小于threshold和
    大于threshold的两部分。
    Args:
        dataframe: 数据集DataFrame
        feature: 特征名称str
        threshold: 特征阈值float
    Returns:
        greater_data: 大于阈值的DataFrame
        less_data: 小于阈值的DataFrame
    """
    greater_data = dataframe[dataframe[feature] > threshold].reset_index(drop=True)
    less_data = dataframe[dataframe[feature] < threshold].reset_index(drop=True)
    return greater_data, less_data

def choose_best_feature(dataframe, features):
    """根据ID3算法选择信息增益最大的特征
    对于特征为连续值的情况，每一个特征用过之后可以在后面继续作为划分特征。
    Args:
        dataframe: 数据集DataFrame
        features: 所有特征名称list
    Returns:
        best_feature: 最优划分特征名称
        best_threshold: 最优划分特征的最优阈值
    """
    base_ent = cal_ent(dataframe)
    best_feature = None
    best_threshold = 0.0
    best_info_gain = 0.0
    for feature in features:
        # print('当前特征为：{}'.format(feature))
        sorted_values = sorted(dataframe[feature].values)
        for i in range(len(sorted_values) - 1):
            threshold = round((sorted_values[i] + sorted_values[i + 1]) / 2, 4)
            greater_data, less_data = split_data(dataframe, feature, threshold)
            prob_g = len(greater_data) / len(dataframe)
            prob_l = len(less_data) / len(dataframe)
            tmp_ent = - prob_g * cal_ent(greater_data) - prob_l * cal_ent(less_data)
            info_gain = base_ent - tmp_ent
            if info_gain > best_info_gain:
                best_feature = feature
                best_info_gain = info_gain
                best_threshold = threshold
            # print(('当前阈值为：{:.4f}，'
            #     '信息增益为：{:.4f}，'
            #     '最佳信息增益为：{:.4f}').format(
            #     threshold,
            #     info_gain,
            #     best_info_gain))
    return best_feature, best_threshold


def majority_label(dataframe):
    """返回DataFrame中label列下出现次数最多的标签
    Args:
        dataframe: 数据集DataFrame
    Returns:
        出现次数最多的标签以及标签种类数量
    """
    # value_counts默认降序，以label为index，以出现次数为value
    value_counts = dataframe['label'].value_counts()
    return value_counts.index.tolist()[0], len(value_counts)


def create_tree(dataframe, features, min_samples_split=3):
    """递归构建决策树
    Args:
        dataframe: 数据集DataFrame
        features: 所有特征名称list
        min_samples_split: 最小划分子集
    Returns:
        my_tree: 决策树dict
    """
    label, label_category_count = majority_label(dataframe)
    # 停止条件1：DataFrame中所有label都相同
    if label_category_count is 1:
        return label
    # 停止条件2：DataFrame包含的样本数小于min_samples_split
    if len(dataframe) < min_samples_split:
        return label

    best_feature, best_threshold = choose_best_feature(dataframe, features)
    tree_node = best_feature + '>' + str(best_threshold)
    my_tree = {tree_node: {}}

    greater_data, less_data = split_data(dataframe, best_feature, best_threshold)

    my_tree[tree_node]['true'] = create_tree(greater_data, features, min_samples_split)
    my_tree[tree_node]['false'] = create_tree(less_data, features, min_samples_split)
    # print(my_tree)
    return my_tree

def classify(input_tree, test_data):
    """对testData进行分类
    Args:
        input_tree: 构建的决策树dict
        test_data: 测试数据dict
    Returns:
        label: testData对应的预测标签
    """
    get_node = list(input_tree.keys())[0]
    feature = get_node.split('>')[0]
    threshold = float(get_node.split('>')[1])

    branches = input_tree[get_node]
    key = 'true' if test_data[feature] > threshold else 'false'

    sub_tree = branches[key]
    if isinstance(sub_tree, dict):
        label = classify(sub_tree, test_data)
    else:
        label = sub_tree
    return label


def save_tree(input_tree, filename):
    """保存决策树"""
    with open(filename, 'wb') as file:
        pickle.dump(input_tree, file)

def load_tree(filename):
    """加载决策树"""
    with open(filename, 'rb') as file:
        return pickle.load(file)

def test_accuracy(input_tree, test_data):
    """测试决策树对测试集的准确率"""
    length = len(test_data)
    score = 0.0
    for i in range(length):
        result = classify(input_tree, test_data.loc[i]) == int(test_data.loc[i]['label'])
        score += int(result) / length
    return round(score, 6)

def test_major(majority, test_data):
    """测试集标签为majority的准确率"""
    length = len(test_data)
    score = 0.0
    for i in range(length):
        result = majority == test_data.loc[i]['label']
        score += int(result) / length
    return round(score, 6)

def post_pruning_tree(input_tree, dataframe, test_data):
    """后剪枝操作
    以递归的方式进行后剪枝
    Args:
        input_tree: 输入需要进行后剪枝的决策树
        dataframe: 训练数据集
        test_data: 测试数据集
    Returns:
        后剪枝决策树
    """
    get_node = list(input_tree.keys())[0]
    feature = get_node.split('>')[0]
    threshold = float(get_node.split('>')[1])

    branches = input_tree[get_node]

    g_data, l_data = split_data(dataframe, feature, threshold)
    g_data_test, l_data_test = split_data(test_data, feature, threshold)
    # 分支判断
    if isinstance(branches['true'], dict):
        input_tree[get_node]['true'] = post_pruning_tree(branches['true'], g_data, g_data_test)
    if isinstance(branches['false'], dict):
        input_tree[get_node]['false'] = post_pruning_tree(branches['false'], l_data, l_data_test)

    majority, _ = majority_label(dataframe)
    # 递归返回
    if test_accuracy(input_tree, test_data) > test_major(majority, test_data):
        return input_tree
    return majority

def main():
    """主函数"""
    train_data, test_data, features = load_dataset()
    tree = create_tree(train_data, features, min_samples_split=2)
    print('未剪枝决策树准确率：{}'.format(test_accuracy(tree, test_data)))
    pruned_tree = post_pruning_tree(tree, train_data, test_data)
    print('后剪枝决策树准确率：{}'.format(test_accuracy(pruned_tree, test_data)))
    # 保存决策树
    save_tree(pruned_tree, 'my_tree.txt')
    # 从文件中读取决策树
    tree_loaded = load_tree('my_tree.txt')
    print('加载剪枝决策树准确率：{}'.format(test_accuracy(tree_loaded, test_data)))


if __name__ == '__main__':
    main()
