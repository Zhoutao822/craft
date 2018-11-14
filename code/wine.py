#%%
#coding=utf-8

from sklearn.datasets import load_wine
from sklearn.mixture import GaussianMixture
rawData = load_wine()

print(rawData['DESCR'])

print(rawData['data'][:5])

print(rawData['target'][:5])

gmm = GaussianMixture(n_components=3)

# gmm.fit(rawData['data'])

pre = gmm.fit_predict(rawData['data'])


print(pre, rawData['target'])