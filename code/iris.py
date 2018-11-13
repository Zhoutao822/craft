#%%
from __future__ import print_function, absolute_import, division
import tensorflow as tf
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

tf.enable_eager_execution()
tfe = tf.contrib.eager
print('Tensorflow version: ', tf.VERSION)
print('Eager mode: ', tf.executing_eagerly())

learning_rate = 0.01
batch_size = 32
num_steps = 1000
display_step = 100

(data, target) = load_iris(return_X_y=True)

x_train, x_test, y_train, y_test = train_test_split(data, target, test_size=0.2, shuffle=True)

def create_iter(x, y):
    y_one_hot = tf.one_hot(y, 3)
    dataset = tf.data.Dataset.from_tensor_slices((x, y_one_hot)).batch(batch_size)
    return tfe.Iterator(dataset)



