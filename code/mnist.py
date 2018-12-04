#%%
from __future__ import absolute_import, print_function, division
import tensorflow as tf
from tensorflow.python.keras import Sequential
from tensorflow.python.keras import layers
from tensorflow import keras

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

print('train size:', x_train.shape, y_train.shape)
print('test size:', x_test.shape, y_test.shape)

print(x_train[0], y_train[0])

#%%

print(y_train[:10])

#%%
dict = {}
for i in range(50000):
    label = y_train[i]
    if (y_train[i,0] not in dict.keys()):
        dict[y_train[i,0]] = 1
    else:
        dict[y_train[i,0]] += 1

print(dict)

#%%
dict2 = {}
for i in range(10000):
    if (y_test[i,0] not in dict2.keys()):
        dict2[y_test[i,0]] = 1
    else:
        dict2[y_test[i,0]] += 1

print(dict2)