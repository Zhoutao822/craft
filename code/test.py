import tensorflow as tf
import numpy as np
from sklearn.datasets import load_iris
from tensorflow import keras
from tensorflow.python.keras import layers


(data, target) = load_iris(return_X_y=True)

one_hot = tf.one_hot(target, depth=3)

model = keras.Sequential([
    layers.Dense(32, 'relu', input_shape=(4,)),
    layers.Dense(32, 'relu'),
    layers.Dense(3, 'softmax')
])

model.compile(
    optimizer=tf.train.AdamOptimizer(0.01),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(
    x=data,
    y=one_hot,
    epochs=20,
    shuffle=True,
    validation_split=0.2,
    steps_per_epoch=20,
    validation_steps=5
)