# Copyright
# License
# ==============================================================================
"""代码功能描述
代码功能细节
"""
#coing=utf-8
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import os

import tensorflow as tf
from tensorflow import keras

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string(
    'data_dir', './cifar10', 'Directory to download and extract CIFAR-10 to.')
FILE_NAMES = ['train', 'validation', 'eval']


def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def convert_to_tfrecord(x, y, output_file):
    """生成tfrecords"""
    with tf.io.TFRecordWriter(output_file) as writer:
        data_length = len(y)
        for i in range(data_length):
            example = tf.train.Example(features=tf.train.Features(
                feature={
                    'image': _bytes_feature(x[i].tobytes()),
                    'label': _int64_feature(y[i])
                }))
            writer.write(example.SerializeToString())
    print('Generate {} success!'.format(output_file))


def main(data_dir):
    print('Start to generate tfrecords in {}.'.format(data_dir))
    (x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()
    split_index = int(len(y_train) * 0.8)
    assert len(x_train) == len(y_train)
    val_data = x_train[split_index:], y_train[split_index:]
    train_data = x_train[:split_index], y_train[:split_index]
    eval_data = x_test, y_test
    for mode, data in zip(FILE_NAMES, [train_data, val_data, eval_data]):
        output_file = os.path.join(data_dir, mode + '.tfrecords')
        x, y = data
        try:
            os.remove(output_file)
        except OSError:
            pass
        convert_to_tfrecord(x, y, output_file)
    print('Done!')


if __name__ == '__main__':
    main(FLAGS.data_dir)