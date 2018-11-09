#%%
#coing=utf-8

from sklearn.datasets import load_breast_cancer

data = load_breast_cancer()

print(data['DESCR'])

print(data['data'].shape, data['target'].shape)
#%%
print(np.sum(data['target']))

#%%
from sklearn.datasets import load_iris

data = load_iris()

print(data['DESCR'])

print(data['data'].shape,data['target'].shape)

#%%
print(data['target'][:130])
