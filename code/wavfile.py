#%%
#coding=utf-8
import scipy.io.wavfile as wavfile
import os
import sys
import tensorflow as tf
import numpy as np

filename1 = 'C://Users//Admin//Desktop//p282_362_clean.wav'
filename2 = '‪C://Users//Admin//Desktop//p282_362_noise.wav'

fm, wav_data = wavfile.read(filename1)

def pre_emph(x, coeff=0.95):
    x0 = tf.reshape(x[0], [1,])
    diff = x[1:] - coeff * x[:-1]
    concat = tf.concat([x0, diff], 0)
    return concat

def sample_random_walk(batch_size, dim):
    rw = np.zeros((batch_size, dim))
    rw[:, 0] = np.random.randn(batch_size)
    for b in range(batch_size):
        for di in range(1, dim):
            rw[b, di] = rw[b, di - 1] + np.random.randn(1)
    # normalize to m=0 std=1
    mean = np.mean(rw, axis=1).reshape((-1, 1))
    std = np.std(rw, axis=1).reshape((-1, 1))
    rw = (rw - mean) / std
    return rw

#%%
print(sample_random_walk(32, 2))