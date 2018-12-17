#%%
import tensorflow as tf
import numpy as np
from tensorflow import keras


(x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()

print(x_train.shape, type(x_train[0, 0, 0, 0]))
