#%%
#coding=utf-8
import numpy as np
from sklearn.datasets import load_wine
from sklearn.mixture import GaussianMixture
rawData = load_wine()

data = rawData['data']
target = rawData['target']

gmm = GaussianMixture(n_components=3)

gmm.means_init = np.array([data[target == i].mean(axis=0) for i in range(3)])

prediction = gmm.fit_predict(data, y=target)

print(prediction)

acc = np.mean(np.equal(prediction, target).astype(np.float))
print('GMM prediction accuracy: {:.4f}'.format(acc))