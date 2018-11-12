#coding=utf-8
#%%
import tensorflow as tf
import numpy as np
from tensorflow.keras.datasets import boston_housing
from sklearn import preprocessing

(x_train, y_train), (x_test, y_test) = boston_housing.load_data()

# scaler = preprocessing.StandardScaler().fit(x_train)
# x_train = scaler.transform(x_train)
# x_test = scaler.transform(x_test)
#%%
column_names = ['CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD',
                'TAX', 'PTRATIO', 'B', 'LSTAT']

def createDict(X):
    return {column_names[i]: X[:, i].ravel() for i in range(len(column_names))}

feature_columns = []
for key in createDict(x_train).keys():
    feature_columns.append(tf.feature_column.numeric_column(key=key))

def input_train():
    dataset = tf.data.Dataset.from_tensor_slices((createDict(x_train), y_train))
    dataset = dataset.shuffle(1000).batch(32).repeat()
    return dataset.make_one_shot_iterator().get_next()

def input_test():
    dataset = tf.data.Dataset.from_tensor_slices((createDict(x_test), y_test))
    dataset = dataset.shuffle(1000).batch(32)
    return dataset.make_one_shot_iterator().get_next()

model = tf.estimator.LinearRegressor(
    feature_columns=feature_columns,
    model_dir="C://Users//Admin//Desktop//model//regressor",
    optimizer=tf.train.FtrlOptimizer(
      learning_rate=0.1,
      l1_regularization_strength=0.001
    ))
#%%
model.train(input_fn=input_train, steps=20000)

#%%
model.evaluate(input_fn=input_test)