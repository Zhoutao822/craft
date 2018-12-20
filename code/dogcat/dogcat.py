#%%
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.preprocessing import image
from tensorflow.keras import layers
from tensorflow.keras import Sequential 

import tensorflow as tf
import pandas as pd
import numpy as np
import os
import shutil

print('Tensorflow version: ', tf.VERSION)

learning_rate = 1e-3
batch_size = 20
epochs = 80
steps_per_epoch = 1000
img_height = 256
img_width = 256
img_channels = 3

# 为了测试代码，我们先不使用整个数据集，而是从原始数据集中划分出一小部分数据进行测试
base_dir = 'C:/Users/Admin/Downloads/dogvscat'
original_dir = os.path.join(base_dir, 'train')

train_dir = os.path.join(base_dir, 'small_train')
eval_dir = os.path.join(base_dir, 'small_eval')
test_dir = os.path.join(base_dir, 'test')

#%%
# if not os.path.exists(eval_dir):
#     os.mkdir(train_dir)
#     os.mkdir(eval_dir)

# for i in range(2500, 12500):
#     name = 'cat.{}.jpg'.format(i)
#     src = os.path.join(original_dir, name)
#     if i < 2000:
#         dst = os.path.join(train_dir, name)
#     else:
#         dst = os.path.join(eval_dir, name)
#     shutil.copyfile(src, dst)

# for i in range(2500, 12500):
#     name = 'dog.{}.jpg'.format(i)
#     src = os.path.join(original_dir, name)
#     if i < 2000:
#         dst = os.path.join(train_dir, name)
#     else:
#         dst = os.path.join(eval_dir, name)
#     shutil.copyfile(src, dst)

#%%
def unison_shuffled_copies(a, b):
    a = np.array(a)
    b = np.array(b)
    assert len(a) == len(b)
    p = np.random.permutation(len(a))
    return a[p], b[p]

files = os.listdir(train_dir)
train_files = [os.path.join(train_dir, name) for name in files]
train_labels = np.array(['dog' in name for name in files]).astype(np.float)
train_files, train_labels = unison_shuffled_copies(train_files, train_labels)

files = os.listdir(eval_dir)
eval_files = [os.path.join(eval_dir, name) for name in files]
eval_labels = np.array(['dog' in name for name in files]).astype(np.float)
eval_files, eval_labels = unison_shuffled_copies(eval_files, eval_labels)

files = ['{}.jpg'.format(i) for i in range(1, 12501)]
test_files = [os.path.join(test_dir, name) for name in files]
test_labels = np.array([-1] * len(files)).astype(np.float)
#%%
def image_input_fn(filenames, labels=None, shuffle=False, repeat_count=1, batch_size=1):
    def _read_img(filename, label=None):
        img_raw = tf.read_file(filename)
        img = tf.image.decode_image(img_raw, channels=3)
        img.set_shape([None, None, None])
        img = tf.image.resize_images(img, [img_height, img_width])
        img = tf.divide(img, 255.)
        img.set_shape([img_height, img_width, img_channels])
        if label is None:
            return img
        else:
            return img, label
    if labels is None:
        dataset = tf.data.Dataset.from_tensor_slices(filenames)
    else:
        dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))
    dataset = dataset.map(_read_img)
    if shuffle:
        dataset = dataset.shuffle(2000)
    dataset = dataset.batch(batch_size).repeat(repeat_count)
    return dataset

# vgg16 = VGG16(
#     weights='imagenet',
#     include_top=False,
#     input_shape=(img_height, img_width, img_channels))
# model = Sequential([
#     vgg16,
#     layers.Flatten(),
#     layers.Dropout(0.5),
#     layers.Dense(1, activation='sigmoid')
# ])
# vgg16.trainable = False

model = Sequential([
    layers.Conv2D(32, 3, 1, padding='SAME', activation='relu', input_shape=(img_height, img_width, img_channels)),
    layers.MaxPool2D(strides=2, padding='SAME'),
    layers.Dropout(0.5),

    layers.Conv2D(64, 3, 1, padding='SAME', activation='relu'),
    layers.MaxPool2D(strides=2, padding='SAME'),
    layers.Dropout(0.5),
    
    layers.Conv2D(128, 3, 1, padding='SAME', activation='relu'),
    layers.MaxPool2D(strides=2, padding='SAME'),
    layers.Dropout(0.5),

    layers.Flatten(),
    layers.Dense(512, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(1, activation='sigmoid')
])

model.summary()

model.compile(
    optimizer=tf.train.AdamOptimizer(learning_rate),
    loss='binary_crossentropy',
    metrics=['acc'])

MODEL_DIR = './model/'
checkpoint_path = MODEL_DIR + "cp-{epoch:04d}.ckpt"
cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path, 
                                                monitor='val_loss',
                                                save_best_only=True,
                                                verbose=1, 
                                                save_weights_only=True, 
                                                period=5)

# model.load_weights('./model/cp-0040.ckpt')

model.fit(
    image_input_fn(
        train_files, 
        train_labels,
        shuffle=True, 
        repeat_count=epochs,
        batch_size=batch_size), 
    validation_data=image_input_fn(
        eval_files,
        eval_labels,
        shuffle=False,
        repeat_count=epochs,
        batch_size=50),
    epochs=epochs,
    steps_per_epoch=steps_per_epoch,
    validation_steps=100,
    callbacks=[cp_callback])
#%%
result = model.predict(
    image_input_fn(
        test_files,
        test_labels,
        shuffle=False,
        batch_size=50), 
        steps=250)

path = './submission.csv'
counter = range(1, len(result) + 1)
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

file = df.to_csv(path_or_buf=None, index=None)
with tf.gfile.Open(path, 'w') as f:
    f.write(file)

print('Mission Accomplished!')