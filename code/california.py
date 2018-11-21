#%%
from sklearn.datasets import fetch_california_housing

rawData = fetch_california_housing()

print(rawData['DESCR'])

#%%
print(rawData['feature_names'])

#%%
from sklearn.datasets import fetch_covtype

(data,target) = fetch_covtype(return_X_y=True)