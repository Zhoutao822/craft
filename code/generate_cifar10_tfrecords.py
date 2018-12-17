# Copyright
# License
# ==============================================================================
"""根据cifar10数据集生成TFRecords文件
版本：
    TensorFlow：1.12
    Python：3.6.7
使用keras.datasets.cifar10.load_data()获得数据，训练集中划分后20%作为验证集，
通过TFRecordWriter写入到三个文件中：train.tfrecords, validation.tfrecords, 
eval.tfrecords，运行时参数data_dir指定生成文件的路径。
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import os

import numpy as np
import tensorflow as tf
from tensorflow import keras

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string(
    'data_dir', './cifar10', 'Directory to generate tfrecords to.')
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
                    # 通过keras获得的数据集的image是uint8类型的数据
                    'image': _bytes_feature(x[i].tobytes()),
                    # 通过keras获得的数据集的label是[xxx, 1]的形状，类型int32，
                    # 需要y[i, 0]获得标签数值，类型转换为int64，
                    # tfrecords只支持Int64List，没有Int32List
                    'label': _int64_feature(y[i, 0].astype(np.int64))
                }))
            writer.write(example.SerializeToString())
    print('Generate {} success!'.format(output_file))


def main(data_dir):
    """
    参数：
        data_dir：tfrecords文件保存路径
    功能：
        主函数，包括生成文件夹，获取数据，划分数据，生成tfrecords文件
    """
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    print('Start to generate tfrecords in {}.'.format(data_dir))
    # 调用keras.datasets.cifar10.load_data()获得数据
    (x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()
    # 这里划分前80%的数据做训练集，20%验证集，理论上要shuffle，
    # 这里我感觉不shuffle也行
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
    # 通过tensorflow的flags产生运行时参数，简单一些
    main(FLAGS.data_dir)