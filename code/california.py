#%%
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf

(data, target) = fetch_california_housing(return_X_y=True)

x_train, x_test, y_train, y_test = train_test_split(data, target, shuffle=True, test_size=0.2)

feature_names = fetch_california_housing()['feature_names']
#%%
feature_columns = []
for name in feature_names:
    feature_columns.append(tf.feature_column.numeric_column(key=name))

def input_fn(x, y, training=True):
    dataframe = pd.DataFrame(data=x, columns=feature_names)
    dataframe['HousePrice'] = y
    if training:
        return tf.estimator.inputs.pandas_input_fn(
            x=dataframe, 
            y=dataframe['HousePrice'],
            batch_size=64, 
            shuffle=True, 
            num_epochs=20)
    else:
        return tf.estimator.inputs.pandas_input_fn(
            x=dataframe,
            y=dataframe['HousePrice'],
            shuffle=False)

dnn = tf.estimator.DNNRegressor(
    feature_columns=feature_columns, 
    hidden_units=[32, 32, 16, 8], 
    model_dir="C://Users//Admin//Desktop//model//DNNRegressor",
    optimizer=tf.train.ProximalAdagradOptimizer(
        learning_rate=0.01, 
        l1_regularization_strength=0.001))

linear = tf.estimator.LinearRegressor(
    feature_columns=feature_columns,
    model_dir="C://Users//Admin//Desktop//model//LinearRegressor",
    optimizer=tf.train.ProximalAdagradOptimizer(
        learning_rate=0.01,
        l1_regularization_strength=0.001))

for i in range(7):
    dnn.train(input_fn=input_fn(x_train, y_train), max_steps=40000)
    dnn.evaluate(input_fn=input_fn(x_test, y_test, training=False))
    linear.train(input_fn=input_fn(x_train, y_train), max_steps=40000)
    linear.evaluate(input_fn=input_fn(x_test, y_test, training=False))

#%%
df = pd.DataFrame(data=data, columns=feature_names)
df['HousePrice'] = target
df = df[(df['MedInc'] < 10) & (df['AveRooms'] < 15) & (df['AveBedrms'] < 4) & (df['Population'] < 8000) & (df['AveOccup'] < 6)]
df.describe()

#%%
print(fetch_california_housing()['DESCR'])

#%%
corr = df.corr()
sns.heatmap(corr)
#%%
df['TotalHouse'] = df['Population'] / df['AveOccup']
df['TotalInc'] = df['MedInc'] / df['Population']
df['AveOtherrms'] = df['AveRooms'] / df['AveBedrms']
for name in df.columns.values.tolist():
    sns.relplot(x=name, y='HousePrice',data=df)


#%%
sns.relplot(x='AveOtherrms', y='HousePrice',data=df)
sns.relplot(x='MedInc', y='HousePrice',data=df)

#%%
def inc_encode(inc):
    if inc < 2:
        return 1.5
    elif inc < 3:
        return 2.5
    elif inc < 4:
        return 3.5
    elif inc < 5:
        return 4.5
    elif inc < 6:
        return 5.5
    elif inc < 7:
        return 6.5
    elif inc < 8:
        return 7.5
    elif inc < 9:
        return 8.5
    elif inc < 10:
        return 9.5
    elif inc < 11:
        return 10.5
    else: 
        return 11.5

df['MedInc'] = df.MedInc.map(inc_encode)

sns.violinplot(x='MedInc', y='HousePrice', data=df)

#%%
sns.violinplot(x=df['HouseAge'])

def age_encode(age):
    if age < 5:
        return 1
    elif age < 10:
        return 2
    elif age < 15:
        return 3
    elif age < 20:
        return 4
    elif age < 25:
        return 5
    elif age < 30:
        return 6
    elif age < 35:
        return 7
    elif age < 40:
        return 8
    elif age < 45:
        return 9
    elif age < 50:
        return 10
    else:
        return 11

df['HouseAge'] = df.HouseAge.map(age_encode)

sns.violinplot(x='HouseAge', y='HousePrice', data=df)

#%%
sns.relplot(x='AveRooms', y='HousePrice',data=df)

#%%
sns.relplot(x='Latitude', y='Longitude',hue='HousePrice', data=df)

#%%
sns.relplot(x='Latitude', y='Longitude',size='HousePrice', data=df[:5000])

#%%
sns.violinplot(x=df['HousePrice'])

#%%
sns.relplot(x='Latitude', y='Longitude',size='HousePrice', data=df[df.HousePrice > 3.0])

sns.relplot(x='Latitude', y='Longitude',size='HousePrice', data=df[df.HousePrice < 3.0])

#%%
for i in range(15):
    sns.relplot(x='Latitude', y='Longitude',hue='HousePrice', data=df.loc[(df.HousePrice > 0.3+0.2*i) & (df.HousePrice < 0.5+0.2*i)])

#%%
for i in range(10):
    sns.relplot(x='Latitude', y='Longitude',hue='HousePrice', data=df[df.HousePrice > 0.3+0.2*i])


#%%
df['AreaPrice'] = -1
for i in range(11):
    for j in range(12):
        rows = (df['Latitude'] >= 32. + i) & \
        (df['Latitude'] < 33. + i) & \
        (df['Longitude'] >= -125. + j) & \
        (df['Longitude'] < -124. + j) 
        df.loc[rows, ['AreaPrice']] = df[rows]['HousePrice'].mean()

df.describe()
#%%
sns.violinplot(x='AreaPrice', y='HousePrice',data=df)
