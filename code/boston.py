#%%
#coding=utf-8

from sklearn.datasets import load_boston
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
pd.set_option('precision', 2)

boston = load_boston()
filepath = boston['filename']
df = pd.read_csv(filepath, skiprows=0, header=1)

data = boston['data']
target = boston['target']

x_train, x_test, y_train, y_test = train_test_split(data, target, test_size=0.2, shuffle=True)

# scaler = preprocessing.StandardScaler().fit(x_train)

# x_train_scale = scaler.transform(x_train)
# x_test_scale = scaler.transform(x_test)

# x_train_scale = np.column_stack((x_train_scale, np.ones(len(x_train_scale))))
# x_test_scale = np.column_stack((x_test_scale, np.ones(len(x_test_scale))))

x_train = np.column_stack((x_train, np.ones(len(x_train))))
x_test = np.column_stack((x_test, np.ones(len(x_test))))

def standLR(x, y):
    '''
        根据公式计算参数w（已经包括bias）
    '''
    xMat = np.mat(x) #将np.array数据转成矩阵便于后续计算
    yMat = np.mat(y).T #对应一列

    xTx = xMat.T * xMat #.T实现矩阵转置
    if np.linalg.det(xTx) == 0.0: #如果矩阵行列式为0说明矩阵不可逆
        print('矩阵不可逆，请使用其他方法！！')
        return
    w = xTx.I * xMat.T * yMat #计算w，w的形状是一列
    return w

def predict(x, w):
    return np.mat(x) * w #根据w计算预测值，预测值也是一列

def mse(pre, y):
    m = y.shape[0]
    yMat = np.mat(y).T
    loss = np.sum(np.square(pre - yMat)) / m #计算MSE，也可以开方获取RMSE
    return loss

w = standLR(x_train, y_train)
pre = predict(x_test, w)
loss = mse(pre, y_test)
print('MSE for testSet is: {:.3f}'.format(loss))
#%%
plt.figure(figsize=(4, 4))
plt.plot([0, 60], [0, 60])
plt.scatter(pre.A, y_test)
plt.show()

