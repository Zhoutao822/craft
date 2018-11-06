#coding=utf-8

print(__doc__)

import tensorflow as tf
from tensorflow.keras.datasets import boston_housing
import random

(x_train, y_train), (x_test, y_test) = boston_housing.load_data()

