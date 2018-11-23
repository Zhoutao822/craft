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

df['TotalHouse'] = df['Population'] / df['AveOccup']
df['TotalInc'] = df['MedInc'] * df['Population']
df['AveOtherrms'] = df['AveRooms'] - df['AveBedrms']

df['AreaPrice'] = -1
for i in range(11):
    for j in range(12):
        rows = (df['Latitude'] >= 32. + i) & \
        (df['Latitude'] < 33. + i) & \
        (df['Longitude'] >= -125. + j) & \
        (df['Longitude'] < -124. + j) 
        df.loc[rows, ['AreaPrice']] = df[rows]['HousePrice'].mean()

df = df.drop(columns=['HouseAge', 'Latitude', 'Longitude'])
df.describe()

#%%
linear_feature_names = ['MedInc', 'AveOtherrms', 'AreaPrice']
linear_feature_columns = []
for name in linear_feature_names:
    linear_feature_columns.append(tf.feature_column.numeric_column(key=name))

dnn_feature_names = df.columns.values.tolist()
dnn_feature_names.remove('HousePrice')
dnn_feature_columns = []
for name in dnn_feature_names:
    dnn_feature_columns.append(tf.feature_column.numeric_column(key=name))

trainset = df.sample(frac=0.8)
testset = df.drop(trainset.index.tolist(), axis=0)

model = tf.estimator.DNNLinearCombinedRegressor(
    linear_feature_columns=linear_feature_columns,
    linear_optimizer=tf.train.FtrlOptimizer(learning_rate=0.01),
    dnn_feature_columns=dnn_feature_columns,
    dnn_optimizer=tf.train.ProximalAdagradOptimizer(
        learning_rate=0.01,
        l1_regularization_strength=0.0001
    ),
    dnn_hidden_units=[64, 32, 16],
    model_dir="C://Users//Admin//Desktop//model//DNNLinearCombinedRegressor",
)

model.train(input_fn=tf.estimator.inputs.pandas_input_fn(
    x=trainset,
    y=trainset['HousePrice'],
    batch_size=64, 
    shuffle=True, 
    num_epochs=100
), max_steps=40000)

model.evaluate(input_fn=tf.estimator.inputs.pandas_input_fn(
    x=testset,
    y=testset['HousePrice'],
    shuffle=False
))
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


