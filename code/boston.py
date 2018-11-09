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

scaler = preprocessing.StandardScaler().fit(x_train)

x_train_scale = scaler.transform(x_train)
x_test_scale = scaler.transform(x_test)

x_train_scale = np.column_stack((x_train_scale, np.ones(len(x_train_scale))))
x_test_scale = np.column_stack((x_test_scale, np.ones(len(x_test_scale))))

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
#%%
w = standLR(x_train, y_train)
pre = predict(x_test, w)
loss = mse(pre, y_test)
print('MSE for testSet is: {:.3f}'.format(loss))
#%%
plt.figure(figsize=(4, 4))
plt.plot([0, 60], [0, 60])
plt.scatter(pre.A, y_test)
plt.show()

#%%
def lwlr(x_point, x, y, k=1.0):
    '''
        Description：
            局部加权线性回归，在待预测点附近的每个点赋予一定的权重，在子集上基于最小均方差来进行普通的回归。
        Notes:
            这其中会用到计算权重的公式，w = e^((x^((i))-x) / -2k^2)
            理解：x为某个预测点，x^((i))为样本点，样本点距离预测点越近，贡献的误差越大（权值越大），越远则贡献的误差越小（权值越小）。
            关于预测点的选取，在我的代码中取的是样本点。其中k是带宽参数，控制w（钟形函数）的宽窄程度，类似于高斯函数的标准差。
            算法思路：假设预测点取样本点中的第i个样本点（共m个样本点），遍历1到m个样本点（含第i个），算出每一个样本点与预测点的距离，
            也就可以计算出每个样本贡献误差的权值，可以看出w是一个有m个元素的向量（写成对角阵形式）。
    '''
    xMat = np.mat(x)
    yMat = np.mat(y).T
    x_point = np.mat(x_point)
    m = np.shape(xMat)[0]
    weights = np.mat(np.eye(m))     # eye()返回一个对角线元素为1，其他元素为0的二维数组，创建权重矩阵weights，该矩阵为每个样本点初始化了一个权重
    for j in range(m):
        diff = x_point - xMat[j, :]         # 计算 testPoint 与输入样本点之间的距离，然后下面计算出每个样本贡献误差的权值
        # print(diff * diff.T)
        weights[j, j] = np.exp(diff * diff.T / (-2.0 * k**2))
        # print(weights[j, j])
    xTx = xMat.T * (weights * xMat)     # 根据矩阵乘法计算 xTx ，其中的 weights 矩阵是样本点对应的权重矩阵
    if np.linalg.det(xTx) == 0.0: #如果矩阵行列式为0说明矩阵不可逆
        print('矩阵不可逆，请使用其他方法！！')
        return
    w = xTx.I * (xMat.T * (weights * yMat))
    return x_point * w

def lwlrPre(x_test, x, y, k=1.0):
    m = x_test.shape[0]
    pre = np.mat(np.zeros((m, 1)))
    for i in range(m):
        pre[i] = lwlr(x_test[i], x, y, k)
    return pre

pre = lwlrPre(x_test_scale, x_train_scale, y_train, k=1.1)
loss = mse(pre, y_test)
print(loss)

#%%
def ridgeRegress(x, y, lam=0.2):
    '''
        Desc：
            这个函数实现了给定 lambda 下的岭回归求解。
            如果数据的特征比样本点还多，就不能再使用上面介绍的的线性回归和局部现行回归了，因为计算 (xTx)^(-1)会出现错误。
            如果特征比样本点还多（n > m），也就是说，输入数据的矩阵x不是满秩矩阵。非满秩矩阵在求逆时会出现问题。
            为了解决这个问题，我们下边讲一下：岭回归，这是我们要讲的第一种缩减方法。
        Args：
            xMat：样本的特征数据，即 feature
            yMat：每个样本对应的类别标签，即目标变量，实际值
            lam：引入的一个λ值，使得矩阵非奇异
        Returns：
            经过岭回归公式计算得到的回归系数
    '''
    xMat = np.mat(x)
    yMat = np.mat(y).T
    xTx = xMat.T * xMat
    demon = xTx + np.eye(xMat.shape[1]) * lam     # 岭回归就是在矩阵 xTx 上加一个 λI 从而使得矩阵非奇异，进而能对 xTx + λI 求逆
    if np.linalg.det(xTx) == 0.0: #如果矩阵行列式为0说明矩阵不可逆
        print('矩阵不可逆，请使用其他方法！！')
        return
    w = xTx.I * (xMat.T * yMat)
    return w

w = ridgeRegress(x_train_scale, y_train, lam=0.2)
pre = predict(x_test_scale, w)
loss = mse(pre, y_test)
print(loss)

plt.figure(figsize=(4, 4))
plt.plot([0, 60], [0, 60])
plt.scatter(pre.A, y_test)
plt.show()   