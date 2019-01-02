#coding=utf-8
# ==============================================================================
"""使用TensorFlow实现文本预测
版本：
    TensorFlow：1.12
    Python：3.6.7
参考：
    https://www.tensorflow.org/tutorials/sequences/text_generation
包含tf.keras和Eager Execution的使用方法，使用 Andrej Karpathy 在 The Unreasonable 
Effectiveness of Recurrent Neural Networks 一文中提供的莎士比亚作品数据集。
"""
#%%
import tensorflow as tf

import numpy as np
import os

print('TensorFlow version: {}'.format(tf.VERSION))
print('Eager Execution: {}'.format(tf.executing_eagerly()))

path_to_file = tf.keras.utils.get_file(
    'shakespeare.txt', 'https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt')

text = open(path_to_file).read()

print ('Length of text: {} characters'.format(len(text)))
print(text[:1000])

vocab = sorted(set(text))
print ('{} unique characters'.format(len(vocab)))

#%%
char2idx = {u:i for i, u in enumerate(vocab)}
idx2char = np.array(vocab)

text_as_int = np.array([char2idx[c] for c in text])

for char,_ in zip(char2idx, range(20)):
    print('{:6s} ---> {:4d}'.format(repr(char), char2idx[char]))

print ('{} ---- characters mapped to int ---- > {}'.format(text[:13], text_as_int[:13]))

#%%
seq_length = 100
examples_per_epoch = len(text)//seq_length

chunks = tf.data.Dataset.from_tensor_slices(text_as_int).batch(seq_length+1, drop_remainder=True)
vocab_size = len(vocab)

# The embedding dimension 
embedding_dim = 256

# Number of RNN units
rnn_units = 1024

def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text

dataset = chunks.map(split_input_target)

BATCH_SIZE = 64

BUFFER_SIZE = 10000
steps_per_epoch = examples_per_epoch//BATCH_SIZE

dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)

if tf.test.is_gpu_available():
    rnn = tf.keras.layers.CuDNNGRU
else:
    import functools
    rnn = functools.partial(
        tf.keras.layers.GRU, recurrent_activation='sigmoid')

def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(vocab_size, embedding_dim, 
                                batch_input_shape=[batch_size, None]),
        rnn(rnn_units,
            return_sequences=True, 
            recurrent_initializer='glorot_uniform',
            stateful=True),
        tf.keras.layers.Dense(vocab_size)
    ])
    return model

model = build_model(
    vocab_size = len(vocab), 
    embedding_dim=embedding_dim, 
    rnn_units=rnn_units, 
    batch_size=BATCH_SIZE)

model.summary()

def loss(labels, logits):
    return tf.keras.backend.sparse_categorical_crossentropy(labels, logits, from_logits=True)

model.compile(
    optimizer = tf.train.AdamOptimizer(),
    loss = loss)

checkpoint_dir = './training_checkpoints'
# Name of the checkpoint files
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_prefix,
    save_weights_only=True)

EPOCHS=20

history = model.fit(
    dataset.repeat(), 
    epochs=EPOCHS, 
    steps_per_epoch=steps_per_epoch, 
    callbacks=[checkpoint_callback])


