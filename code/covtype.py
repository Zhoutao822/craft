#%%
from sklearn.datasets import fetch_covtype
from sklearn.model_selection import train_test_split
import seaborn as sns
import tensorflow as tf
import pandas as pd
import numpy as np

(data, target) = fetch_covtype(return_X_y=True)

x_train, x_test, y_train, y_test = train_test_split(data, target, shuffle=True, test_size=0.2)

feature_names = [
    'Elevation', 'Aspect', 'Slope', 
    'Horizontal_Distance_To_Hydrology', 
    'Vertical_Distance_To_Hydrology', 
    'Horizontal_Distance_To_Roadways', 
    'Hillshade_9am', 'Hillshade_Noon', 
    'Hillshade_3pm', 'Horizontal_Distance_To_Fire_Points', 
    'Wilderness_Area', 'Soil_Type']

feature_columns = []
for i in range(10):
    feature_columns.append(tf.feature_column.numeric_column(key=feature_names[i]))
feature_columns.append(tf.feature_column.numeric_column(key=feature_names[10], shape=(4,)))
feature_columns.append(tf.feature_column.numeric_column(key=feature_names[11], shape=(40,)))


def input_fn(x, y, training=True):
    y = y - 1
    inputs = {}
    for i in range(10):
        inputs[feature_names[i]] = np.array(x[:, i])
    inputs[feature_names[10]] = np.array(x[:, 10:14])
    inputs[feature_names[11]] = np.array(x[:, 14:])
    if training:
        return tf.estimator.inputs.numpy_input_fn(
            x=inputs,
            y=y,
            batch_size=64,
            shuffle=True,
            num_epochs=20
        )
    else:
        return tf.estimator.inputs.numpy_input_fn(
            x=inputs,
            y=y,
            shuffle=False
        )

model = tf.estimator.DNNClassifier(
    hidden_units=[64, 64, 32, 16],
    feature_columns=feature_columns,
    n_classes=7,
    model_dir="C://Users//Admin//Desktop//model//DNNClassifier",
    optimizer=tf.train.ProximalAdagradOptimizer(
        learning_rate=0.01,
        l1_regularization_strength=0.0001
    )
)

for i in range(5):
    model.train(input_fn=input_fn(x_train, y_train), max_steps=800000)
    print(model.evaluate(input_fn=input_fn(x_test, y_test, training=False)))

#%%
from __future__ import print_function, division, absolute_import
import tensorflow as tf
import numpy as np
from sklearn.datasets import fetch_covtype
from tensorflow import keras
from tensorflow.python.keras import layers

(data, target) = fetch_covtype(return_X_y=True)

target_onehot = tf.one_hot(target, depth=7)

BATCH_SIZE = 64
EPOCHS = 50
STEPS_PER_EPOCH = 8000

dataset = tf.data.Dataset.from_tensor_slices((data, target_onehot))
dataset = dataset.batch(BATCH_SIZE).shuffle(10000).repeat()

model = keras.Sequential([
    layers.Dense(units=64, activation='relu', input_shape=(54,)),
    layers.Dense(units=64, activation='relu'),
    layers.Dense(units=32, activation='relu'),
    layers.Dense(units=16, activation='relu'),
    layers.Dense(units=7, activation='softmax')
])

model.compile(loss='categorical_crossentropy',
    optimizer=tf.keras.optimizers.AdamOptimizer(0.001),
    metrics=['accuracy'])

early_stop = tf.keras.callbacks.EarlyStopping(
    patience=5, 
    monitor='val_loss', 
    mode='auto'
)

ckpt_callback = tf.keras.callbacks.ModelCheckpoint(
    "./checkpoint/cp-{epoch:04d}.ckpt",
    verbose=1,
    save_weights_only=True,
    period=10
)

tb_callback = tf.keras.callbacks.TensorBoard(
    log_dir='./log',
    batch_size=BATCH_SIZE
)

class PrintLoss(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs):
        print('Epoch: {:03d} - loss: {:.5f} - acc: {:.5f} - \
        val_loss: {:.5f} - val_acc: {:.5f}'.format(epoch + 1, logs['loss'], logs['acc'], logs['val_loss'], logs['val_acc']))

history = model.fit(
    dataset,
    epochs=EPOCHS,
    steps_per_epoch=STEPS_PER_EPOCH,
    validation_split=0.2,
    verbose=0,
    callbacks=[early_stop, ckpt_callback, tb_callback, PrintLoss()]
)
