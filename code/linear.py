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

def createDict(X):
    return {
        'CRIM': X[:, 0].ravel(),
        'ZN': X[:, 1].ravel(),
        'INDUS': X[:, 2].ravel(),
        'CHAS': X[:, 3].ravel(),
        'NOX': X[:, 4].ravel(),
        'RM': X[:, 5].ravel(),
        'AGE': X[:, 6].ravel(),
        'DIS': X[:, 7].ravel(),
        'RAD': X[:, 8].ravel(),
        'TAX': X[:, 9].ravel(),
        'PTRATIO': X[:, 10].ravel(),
        'B': X[:, 11].ravel(),
        'LSTAT': X[:, 12].ravel(),
    }

feature_columns = []
for key in createDict(x_train).keys():
    feature_columns.append(tf.feature_column.numeric_column(key=key))

def input_train():
    dataset = tf.data.Dataset.from_tensor_slices((createDict(x_train), y_train))
    dataset = dataset.shuffle(1000).batch(64).repeat()
    return dataset.make_one_shot_iterator().get_next()

def input_test():
    dataset = tf.data.Dataset.from_tensor_slices((createDict(x_test), y_test))
    dataset = dataset.shuffle(1000).batch(64)
    return dataset.make_one_shot_iterator().get_next()

model = tf.estimator.LinearRegressor(
    feature_columns=feature_columns,
    model_dir="C://Users//Admin//Desktop//model1"
    )
#%%
model.train(input_fn=input_train, steps=20000)

#%%
model.evaluate(input_fn=input_test)