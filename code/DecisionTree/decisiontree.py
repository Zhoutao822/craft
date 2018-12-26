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

print(rawData['feature_names'])

df = pd.DataFrame(data, columns=rawData['feature_names'])

df.describe()
#%%
df['label'] = target

df.describe()

