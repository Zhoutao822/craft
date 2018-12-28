#!/usr/bin/python3
#coding=utf-8
# ==============================================================================
"""使用Python实现决策树
版本：
    Python：3.6.7
参考：
    https://github.com/apachecn/AiLearning
"""
#%%
import pandas as pd
from sklearn.datasets import load_wine
rawData = load_wine()

data = rawData['data']
target = rawData['target']

print(rawData['DESCR'])

features = rawData['feature_names']
# 使用Pandas便于计算和处理数据
df = pd.DataFrame(data, columns=rawData['feature_names'])

df['label'] = target

df.describe()

#%%
from math import log

def calEnt(dataFrame, label):
    """计算以label为目标的信息熵
    
    Args:
        dataFrame: 数据集DataFrame
        label: 目标标签名称str
    
    Returns:
        ent_data: 信息熵的值
    """
    ent_data = 0.0
    # value_counts返回label列下的值和对应的出现次数，Series类型
    value_counts = dataFrame[label].value_counts()
    # Series可以使用items()遍历
    for _, value in value_counts.items():
        p = value / len(dataFrame)
        ent_data += - p * log(p, 2)
    return ent_data

print(calEnt(df, 'label'))

#%%
def splitData(dataFrame, feature, threshold):
    """根据阈值划分数据集
    
    对于连续值的特征，采用插队的方式选出threshold，将数据集划分为小于threshold和
    大于threshold的两部分。
    Args:
        dataFrame: 数据集DataFrame
        feature: 特征名称str
        threshold: 特征阈值float

    Returns:
        greater_data: 大于阈值的DataFrame
        less_data: 小于阈值的DataFrame
    """
    greater_data = dataFrame[dataFrame[feature] > threshold].reset_index(drop=True)
    less_data = dataFrame[dataFrame[feature] < threshold].reset_index(drop=True)
    return greater_data, less_data

g, l = splitData(df, 'alcohol', 13.0001)

l.describe()

#%%
def chooseBestFeature(dataFrame, features, label):
    """根据ID3算法选择信息增益最大的特征
    
    对于特征为连续值的情况，每一个特征用过之后可以在后面继续作为划分特征。

    Args:
        dataFrame: 数据集DataFrame
        features: 所有特征名称list
        label: 标签列名称str

    Returns: 
        bestFeature: 最优划分特征名称 
        bestThreshold: 最优划分特征的最优阈值
    """
    baseEnt = calEnt(dataFrame, label)
    bestFeature = None
    bestThreshold = 0.0
    bestInfoGain = 0.0
    for feature in features:
        # print('当前特征为：{}'.format(feature))
        sorted_values = sorted(dataFrame[feature].values)
        for i in range(len(sorted_values) - 1):
            threshold = round((sorted_values[i] + sorted_values[i + 1]) / 2, 4)
            greater_data, less_data = splitData(dataFrame, feature, threshold)
            prob_g = len(greater_data) / len(dataFrame)
            prob_l = len(less_data) / len(dataFrame)
            tmpEnt = - prob_g * calEnt(greater_data, label) - prob_l * calEnt(less_data, label)
            infoGain = baseEnt - tmpEnt
            if infoGain > bestInfoGain:
                bestFeature = feature
                bestInfoGain = infoGain
                bestThreshold = threshold
            # print(('当前阈值为：{:.4f}，'
            #     '信息增益为：{:.4f}，'
            #     '最佳信息增益为：{:.4f}').format(
            #     threshold, 
            #     infoGain, 
            #     bestInfoGain))
    return bestFeature, bestThreshold

print(chooseBestFeature(g, features, 'label'))
print(chooseBestFeature(l, features, 'label'))

#%%
def majorityLabel(dataFrame, label):
    """返回DataFrame中label列下出现次数最多的标签
    
    Args:
        dataFrame: 数据集DataFrame
        label: 标签列名称str
    
    Returns:
        出现次数最多的标签
    """
    # value_counts默认降序，以label为index，以出现次数为value
    value_counts = dataFrame[label].value_counts()
    return value_counts.index.tolist()[0], len(value_counts)

print(majorityLabel(l, 'label'))

#%%
from sklearn.utils import shuffle

def createTree(dataFrame, features, label, min_samples_split=3):
    """递归构建决策树
    
    Args:
        dataFrame: 数据集DataFrame
        features: 所有特征名称list
        label: 标签列名称str
        min_samples_split: 最小划分子集

    Returns:
        myTree: 决策树dict
    """
    majority_label, label_category_count = majorityLabel(dataFrame, label)
    # 停止条件1：DataFrame中所有label都相同
    if label_category_count is 1:
        return majority_label
    # 停止条件2：DataFrame包含的样本数小于min_samples_split
    if len(dataFrame) < min_samples_split:
        return majority_label

    bestFeature, bestThreshold = chooseBestFeature(dataFrame, features, label)
    tree_node = bestFeature + '>' + str(bestThreshold)
    myTree = {tree_node: {}}

    greater_data, less_data = splitData(dataFrame, bestFeature, bestThreshold)

    myTree[tree_node]['true'] = createTree(greater_data, features, label, min_samples_split)
    myTree[tree_node]['false'] = createTree(less_data, features, label, min_samples_split)
    # print(myTree)
    return myTree

tree = createTree(df, features, 'label', min_samples_split=3)
print(tree)

#%%
def classify(inputTree, testData):
    """对testData进行分类
    
    Args:
        inputTree: 构建的决策树dict
        testData: 测试数据dict
    
    Returns:
        label: testData对应的预测标签
    """
    get_node = list(inputTree.keys())[0]
    feature = get_node.split('>')[0]
    threshold = float(get_node.split('>')[1])

    branches = inputTree[get_node]
    key = 'true' if testData[feature] > threshold else 'false'

    subTree = branches[key]
    if isinstance(subTree, dict):
        label = classify(subTree, testData)
    else:
        label = subTree
    return label
score = 0.0
for i in range(178):
    result = classify(tree, df.loc[i]) == int(df.loc[i]['label'])
    score += int(result) / 178
print(score)

#%%
import pickle
def saveTree(inputTree, filename):
    with open(filename, 'wb') as f:
        pickle.dump(inputTree, f)

def loadTree(filename):
    with open(filename, 'rb') as f:
        pickle.load(f)
#%%
def testAccuracy(inputTree, testData, label):
    length = len(testData)
    score = 0.0
    for i in range(length):
        result = classify(inputTree, testData.loc[i]) == int(testData.loc[i][label])
        score += int(result) / length
    return round(score, 6)

testAccuracy(tree, df, 'label')

def testMajor(majority, testData, label):
    length = len(testData)
    score = 0.0
    for i in range(length):
        result = majority == testData.loc[i][label]
        score += int(result) / length
    return round(score, 6)

testMajor(2, df, 'label')

#%%
def postPruningTree(inputTree, dataFrame, testData, label):
    get_node = list(inputTree.keys())[0]
    feature = get_node.split('>')[0]
    threshold = float(get_node.split('>')[1])

    branches = inputTree[get_node]

    g_data, l_data = splitData(dataFrame, feature, threshold)
    g_data_test, l_data_test = splitData(testData, feature, threshold)
    if isinstance(branches['true'], dict):
        inputTree[get_node]['true'] = postPruningTree(branches['true'], g_data, g_data_test, label)
    if isinstance(branches['false'], dict):
        inputTree[get_node]['false'] = postPruningTree(branches['false'], l_data, l_data_test, label)

    majority, _ = majorityLabel(dataFrame, label)
    if testAccuracy(inputTree, testData, label) > testMajor(majority, testData, label):
        return inputTree
    return majority

postPruningTree(tree, df, df[:80], 'label')
