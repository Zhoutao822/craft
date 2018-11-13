#%%
#coding=utf-8

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt

(data, target) = load_breast_cancer(return_X_y=True)

x_train, x_test, y_train, y_test = train_test_split(data, target, test_size=0.2, shuffle=True)

X0 = np.array([x_train[i] for i in range(len(x_train)) if y_train[i] == 0])
X1 = np.array([x_train[i] for i in range(len(x_train)) if y_train[i] == 1])

mu0 = np.mean(X0, axis=0)
mu1 = np.mean(X1, axis=0)

sigma0 = np.mat(np.zeros((X0.shape[1], X0.shape[1]))) 
sigma1 = np.mat(np.zeros((X1.shape[1], X1.shape[1])))

for i in range(X0.shape[0]):
    sigma0 += np.mat(X0[i] - mu0).T * np.mat(X0[i] - mu0)

for j in range(X1.shape[0]):
    sigma1 += np.mat(X1[i] - mu1).T * np.mat(X1[i] - mu1)

Sw = sigma0 + sigma1

w = Sw.I * np.mat(mu0 - mu1).T

center0 = (np.mat(mu0) * w).getA()
center1 = (np.mat(mu1) * w).getA()

result = []
pre = np.mat(x_test) * w
for p in pre:
    if abs(p - center0) > abs(p - center1):
        result.append(1)
    else:
        result.append(0)
print('Test accuracy: {:.4f}'.format(np.mean(np.equal(result, y_test).astype(np.float))))