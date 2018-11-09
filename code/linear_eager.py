#coding=utf-8
#%%
from __future__ import absolute_import, division, print_function

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import boston_housing
from sklearn import preprocessing
tf.enable_eager_execution()
tfe = tf.contrib.eager

print('Tensorflow version: ', tf.__version__)
print('Eager mode: ', tf.executing_eagerly())

#%%
(x_train, y_train), (x_test, y_test) = boston_housing.load_data()

scaler = preprocessing.StandardScaler().fit(x_train)
x_train_scale = scaler.transform(x_train)
x_test_scale = scaler.transform(x_test)

n_train = len(x_train)
n_test = len(x_test)
n_features = x_train.shape[1]

learning_rate = 0.001
display_step = 1000
num_steps = 10000
batch_size = 64

W = tfe.Variable(tf.zeros([n_features, 1]), name='weights')
b = tfe.Variable(tf.zeros([1]), name='bias')

dataset_train = tf.data.Dataset.from_tensor_slices((x_train_scale, y_train)).batch(batch_size).shuffle(1000)
dataset_test = tf.data.Dataset.from_tensor_slices((x_test_scale, y_test))
dataset_train_iter = tfe.Iterator(dataset_train)
dataset_test_iter = tfe.Iterator(dataset_test)

print(x_train.shape, W, b)

#%%
def lr(inputs):
    return tf.matmul(inputs, W) + b

# 计算MSE
def mse(model_fn, inputs, labels):
    return tf.reduce_mean(tf.square(model_fn(inputs) - labels))

optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)

grad = tfe.implicit_gradients(mse)

average_loss = 0.
for step in range(num_steps):
    try:
        d = dataset_train_iter.next()
    except StopIteration:
        dataset_train_iter = tfe.Iterator(dataset_train)
        d = dataset_train_iter.next()

    x_batch = tf.cast(d[0], np.float32)
    y_batch = tf.cast(d[1], np.float32)
    batch_loss = mse(lr, x_batch, y_batch)
    average_loss += batch_loss

    optimizer.apply_gradients(grad(lr, x_batch, y_batch))

    if((step + 1) % display_step == 0 or step == 0):
        if step > 0:
            average_loss /= display_step
        print("Step:", '%05d' % (step + 1), " loss=",
              "{:.3f}".format(average_loss))
        average_loss = 0.
#%%
print(W.numpy(), b.numpy())

#%%
def predict(x, w):
    return np.mat(x) * w #根据w计算预测值，预测值也是一列

def mses(pre, y):
    m = y.shape[0]
    yMat = np.mat(y).T
    loss = np.sum(np.square(pre - yMat)) / m #计算MSE，也可以开方获取RMSE
    return loss

pre = predict(x_test_scale, W.numpy())
loss = mses(pre, y_test)
print(loss)