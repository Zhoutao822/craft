#%%
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

from tensorflow.keras.preprocessing import image
from tensorflow.keras import layers
from tensorflow.keras import Sequential 

import tensorflow as tf
import pandas as pd
import numpy as np
import os
import shutil

print('Tensorflow version: ', tf.VERSION)

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

print(x_train.shape, x_test.shape, y_train.shape, y_test.shape)
