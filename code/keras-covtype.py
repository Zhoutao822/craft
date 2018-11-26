#%%
import tensorflow as tf
import numpy as np
from sklearn.datasets import fetch_covtype
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from tensorflow import keras
from tensorflow.python.keras import layers

(data, target) = fetch_covtype(return_X_y=True)

scaler = preprocessing.StandardScaler().fit(X=data)

data = scaler.transform(data)

x_train, x_test, y_train, y_test = train_test_split(data, target, shuffle=True, test_size=0.2)

y_train_onehot = tf.one_hot(y_train - 1, depth=7)
y_test_onehot = tf.one_hot(y_test - 1, depth=7)
target_onehot = tf.one_hot(target - 1, depth=7)

BATCH_SIZE = 64
EPOCHS = 30
STEPS_PER_EPOCH = 6000

trainset = tf.data.Dataset.from_tensor_slices((x_train, y_train_onehot))
trainset = trainset.batch(BATCH_SIZE).repeat()

testset = tf.data.Dataset.from_tensor_slices((x_test, y_test_onehot))
testset = testset.batch(BATCH_SIZE).repeat()

model = keras.Sequential([
    layers.Dense(units=64, activation='relu', input_shape=(54,)),
    layers.Dense(units=64, activation='relu'),
    layers.Dense(units=32, activation='relu'),
    layers.Dense(units=16, activation='relu'),
    layers.Dense(units=7, activation='softmax')
])

model.compile(loss='categorical_crossentropy',
    optimizer=tf.train.AdamOptimizer(0.01),
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
    trainset,
    epochs=EPOCHS,
    steps_per_epoch=STEPS_PER_EPOCH,
    validation_data=testset,
    validation_steps=STEPS_PER_EPOCH // 4,
    verbose=0,
    callbacks=[PrintLoss()]
)

# model.fit(
#     x=data,
#     y=target_onehot,
#     epochs=EPOCHS,
#     shuffle=True,
#     validation_split=0.2,
#     steps_per_epoch=STEPS_PER_EPOCH,
#     validation_steps=STEPS_PER_EPOCH // 4,
#     callbacks=[ckpt_callback]
# )