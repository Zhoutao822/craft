#%%
#coding=utf-8

import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn import preprocessing
from sklearn.model_selection import train_test_split

rawData = load_breast_cancer()

data = rawData['data']
target = rawData['target']

x_train, x_test, y_train, y_test = train_test_split(data, target, test_size=0.2, shuffle=True)

x_train = np.column_stack((x_train, np.ones(len(x_train))))
x_test = np.column_stack((x_test, np.ones(len(x_test))))
#%%

# 终极小tips，feature_columns的key不能包含空格在名称中，否则报错not valid scope name
column_names = [name.replace(' ', '') for name in rawData['feature_names']]

def createDict(X):
    return {column_names[i]: X[:, i].ravel() for i in range(len(column_names))}

feature_columns = []
for key in column_names:
    feature_columns.append(tf.feature_column.numeric_column(key=key))

# 使用一个函数代替input_train和input_test
def input_fn(x, y, training=True):
    dataset = tf.data.Dataset.from_tensor_slices((createDict(x), y))
    if training:
        dataset = dataset.shuffle(1000).batch(32).repeat()
    else:
        dataset = dataset.batch(32)
    return dataset.make_one_shot_iterator().get_next()

model = tf.estimator.LinearClassifier(
    n_classes=2, # 默认为2，可以不写，其他分类需要指定
    feature_columns=feature_columns, # 指定特征列
    model_dir="C://Users//Admin//Desktop//model//classifier", # 指定模型保存的位置，包括了checkpoint和tensorboard数据
    optimizer=tf.train.FtrlOptimizer(
      learning_rate=0.01,
      l1_regularization_strength=0.001 # 增加l1正则化，系数0.001，使参数中产生更多的0，可以提高泛化性能
    ))

model.train(input_fn=lambda: input_fn(x_train, y_train), steps=10000)

model.evaluate(input_fn=lambda: input_fn(x_test, y_test, training=False))


#%%
def sigmoid(x):
    return 1.0 / (1 + np.exp(-x))

def standGrad(x, y):
    xMat = np.mat(x)
    yMat = np.mat(y).T
    n = xMat.shape[1]
    alpha = 0.01
    steps = 1000
    weights = np.ones((n, 1))
    # 关键部分，根据迭代次数steps，每次迭代都使用全部数据，公式计算
    for i in range(steps):
        pre = sigmoid(xMat * weights)
        error = pre - yMat
        weights -= alpha * xMat.T * error
    return weights

# sigmoid函数计算得到预测值为1的概率，若概率大于0.5（也可以设置为其他值，
# 避免类别不均衡问题），则认为预测值为1
def predict(x, w):
    xMat = np.mat(x)
    pro = sigmoid(xMat * w) 
    pre = [1 if p > 0.5 else 0 for p in pro]
    return pro, pre

def accuracy(pre, y):
    return np.sum(np.equal(pre, y).astype(np.float))/len(pre)

w = standGrad(x_train, y_train)
pro, pre = predict(x_test, w)
print('Testset prediction accuracy: {:.3f}'.format(accuracy(pre, y_test)))


#%%
def stocGrad(x, y, steps=300):
    m, n = x.shape
    weights = np.ones(n)
    for i in range(steps):
        index = list(range(m))
        for j in range(m):
            rand_index = int(np.random.uniform(0, len(index)))
            alpha = 4 / (1.0 + i + j) + 0.01
            pre = sigmoid(np.sum(x[index[rand_index]] * weights))
            error = pre - y[index[rand_index]]
            weights -= alpha * error * x[index[rand_index]]
            del(index[rand_index])
    return np.mat(weights).T

w = stocGrad(x_train, y_train)
pro, pre = predict(x_test, w)
print('Testset prediction accuracy: {:.3f}'.format(accuracy(pre, y_test)))