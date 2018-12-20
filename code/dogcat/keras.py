# Copyright
# License
# ==============================================================================
"""使用CPU进行训练的main文件
版本：
    TensorFlow：1.12
    Python：3.6.7
定义运行时参数，仅使用CPU进行训练和验证
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os

import numpy as np
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.INFO)
FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string(
    'data_dir', './cifar10', 'Directory to generate tfrecords to.')
tf.app.flags.DEFINE_string(
    'job_dir', './tmp', 'Directory to generate model to.')
tf.app.flags.DEFINE_integer(
    'train_steps', 2000, 'Train steps.')
tf.app.flags.DEFINE_integer(
    'eval_steps', 100, 'Eval steps.')  # eval_steps * eval_batch_size最好等于eval数据集大小
tf.app.flags.DEFINE_integer(
    'train_batch_size', 128, 'Train batch size.')
tf.app.flags.DEFINE_integer(
    'eval_batch_size', 100, 'Eval batch size.')    
tf.app.flags.DEFINE_integer(
    'num_layers', 44, 'The number of layers of the model.') 
tf.app.flags.DEFINE_float(
    'learning_rate', 0.1, 'Learning rate value.') 