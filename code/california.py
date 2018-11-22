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

df.describe()

#%%
corr = df.corr()
sns.heatmap(corr)

sns.relplot(x='MedInc', y='HousePrice',data=df)

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
sns.relplot(x='Latitude', y='Longitude',size='HousePrice', data=df.loc[(df.HousePrice > 0.8) & (df.HousePrice < 2.5)])

#%%
for i in range(10):
    sns.relplot(x='Latitude', y='Longitude',hue='HousePrice', data=df[df.HousePrice > 0.3+0.5*i])
