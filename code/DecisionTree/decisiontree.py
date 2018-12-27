#!/usr/bin/python3
#coding=utf-8
# ==============================================================================
"""使用Python和Numpy实现决策树
版本：
    Python：3.6.7
参考：
    https://github.com/apachecn/AiLearning
"""
#%%
import numpy as np
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
data = df['label'].value_counts()

for index, value in data.items():
    print(index, value)

print(len(df))

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
    greater_data = dataFrame[dataFrame[feature] > threshold]
    less_data = dataFrame[dataFrame[feature] < threshold]
    return greater_data, less_data

g, l = splitData(df, 'alcohol', 13.0001)

l.describe()

#%%
def chooseBestFeature(dataFrame, features, label):
    """根据ID3算法选择信息增益最大的特征
    
    对于特征为连续值的情况，每一个特征用过之后可以在后面继续作为划分特征。

    Args:
        dataFrame: 数据集DataFrame

    Returns: 
        bestFeature: 最优划分特征名称 
        bestThreshold: 最优划分特征的最优阈值
    """
    baseEnt = calEnt(dataFrame, label)
    bestFeature = None
    bestThreshold = 0.0
    bestInfoGain = 0.0
    for feature in features:
        sorted_values = sorted(dataFrame[feature].values)
        for i in range(len(sorted_values) - 1):
            threshold = (sorted_values[i] + sorted_values[i + 1]) / 2
            greater_data, less_data = splitData(dataFrame, feature, threshold)
            prob_g = len(greater_data) / len(dataFrame)
            prob_l = len(less_data) / len(dataFrame)
            tmpEnt = - prob_g * calEnt(greater_data, label) - prob_l * calEnt(less_data, label)
            infoGain = baseEnt - tmpEnt
            if infoGain > bestInfoGain:
                bestFeature = feature
                bestInfoGain = infoGain
                bestThreshold = threshold
    return bestFeature, bestThreshold

print(chooseBestFeature(df, features, 'label'))
#%%

