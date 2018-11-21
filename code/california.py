#%%
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


(data, target) = fetch_california_housing(return_X_y=True)

feature_names = fetch_california_housing()['feature_names']

print(feature_names)

#%%
df = pd.DataFrame(data=data, columns=feature_names)
df['HousePrice'] = target

df.describe()

#%%
corr = df.corr()
sns.heatmap(corr)

sns.relplot(x='MedInc', y='HousePrice',data=df.loc[:,['MedInc', 'HousePrice']])

#%%
sns.relplot(x='AveRooms', y='HousePrice',data=df.loc[:,['AveRooms', 'HousePrice']])
