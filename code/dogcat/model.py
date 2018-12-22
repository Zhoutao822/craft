#%%
import numpy as np
from tensorflow import keras
import tensorflow as tf
import h5py
import pandas as pd
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

x_train = []
y_train = []
x_test = []
x_index = []
for filename in ['gap_InceptionV3.h5', 'gap_ResNet50.h5', 'gap_MobileNetV2.h5']:
    with h5py.File(filename, 'r') as h:
        x_train.append(np.array(h['train']))
        x_test.append(np.array(h['test']))
        y_train = np.array(h['label'])
        x_index = np.array(h['index'])

x_train = np.concatenate(x_train, axis=1)
x_test = np.concatenate(x_test, axis=1)
y_train = np.array(y_train)
x_index = np.array(x_index)
print(x_train.shape, x_test.shape, y_train.shape, x_index.shape)

def unison_shuffled_copies(a, b):
    a = np.array(a)
    b = np.array(b)
    assert len(a) == len(b)
    p = np.random.permutation(len(a))
    return a[p], b[p]

x_train, y_train = unison_shuffled_copies(x_train, y_train)

model = keras.Sequential([
    keras.layers.Dropout(0.5, input_shape=(x_train.shape[-1],)),
    keras.layers.Dense(1, activation='sigmoid')
])

model.compile(
    loss='binary_crossentropy',
    optimizer=tf.train.AdamOptimizer(),
    metrics=['acc']
)
#%%
model.fit(
    x=x_train,
    y=y_train,
    batch_size=128,
    epochs=8,
    validation_split=0.2,
    callbacks=[keras.callbacks.TensorBoard(log_dir='./log')]
)

model.save('model.h5')

#%%
result = model.predict(x_test)

path = './submission.csv'
counter = x_index
result = np.array(result, np.float)
result = np.squeeze(result)

def limit(x):
    if x < 0.005:
        return 0.005
    elif x > 0.995:
        return 0.995
    else:
        return x

df = pd.DataFrame({'id': counter, 'label': result})
df['label'] = df['label'].map(limit)
df = df.sort_values(by='id')
file = df.to_csv(path_or_buf=None, index=None)
with tf.gfile.Open(path, 'w') as f:
    f.write(file)

print('Mission Accomplished!')