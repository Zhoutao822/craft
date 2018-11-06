#coding=utf-8

print(__doc__)

import tensorflow as tf
from tensorflow.keras.datasets import boston_housing
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.datasets import mnist
import random

(x_train, y_train), (x_test, y_test) = boston_housing.load_data()
(x_train, y_train), (x_test, y_test) = cifar10.load_data()
(x_train, y_train), (x_test, y_test) = mnist.load_data()
