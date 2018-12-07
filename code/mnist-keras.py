#%%
from __future__ import absolute_import, print_function, division
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


print('Tensorflow version: ', tf.VERSION)

learning_rate = 1e-4
num_steps = 20000
batch_size = 64
display_step = 100

num_classes = 10

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train , x_test = x_train / 255. , x_test / 255.
x_train = tf.reshape(x_train, [-1, 28, 28, 1])
x_test = tf.reshape(x_test, [-1, 28, 28, 1])
print('train size:', x_train.shape, y_train.shape)
print('test size:', x_test.shape, y_test.shape)

dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train)).shuffle(1000).batch(batch_size).repeat()

model = keras.Sequential([
    layers.Conv2D(32, 5, padding='SAME', activation='relu', input_shape=(28, 28, 1)),
    layers.MaxPool2D(2, padding='SAME'),
    layers.Conv2D(64, 5, padding='SAME', activation='relu'),
    layers.MaxPool2D(2, padding='SAME'),

    layers.Flatten(),
    layers.Dense(1024, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(lr=learning_rate),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

model.fit(dataset, epochs=20, steps_per_epoch=1000, use_multiprocessing=True)
#%%
model.evaluate(x_test, y_test, steps=1)