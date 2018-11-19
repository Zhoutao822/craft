
#%%
from sklearn.datasets import fetch_california_housing

rawData = fetch_california_housing()

print(rawData['DESCR'])

#%%
print(rawData['feature_names'])

#%%
from sklearn.datasets import fetch_covtype

data = fetch_covtype()

print(data['DESCR'])
print(data['feature_names'])