# Copyright
# License
# ==============================================================================
"""生成CIFAR10 Dataset
版本：
    TensorFlow：1.12
    Python：3.6.7
读取tfrecords文件，对图片和标签的数据类型进行调整，对图片进行扰乱处理，比如裁剪、
亮度调整、对比度调整和翻转等操作，shuffle和batch，make_batch返回一个batch的数据，
此部分代码改动较少。
"""
import os

import tensorflow as tf

HEIGHT = 32
WIDTH = 32
DEPTH = 3


class Cifar10DataSet(object):
    """通过一个类来管理dataset"""
    def __init__(self, data_dir, subset='train', use_distortion=True):
        self.data_dir = data_dir
        self.subset = subset
        self.use_distortion = use_distortion

    def get_filenames(self):
        if self.subset in ['train', 'validation', 'eval']:
            return [os.path.join(self.data_dir, self.subset + '.tfrecords')]
        else:
            raise ValueError('Invalid data subset {}'.format(self.subset))

    def parser(self, example):
        """读取tfrecords文件，类型转换，shape调整"""
        features = tf.parse_single_example(
            example, 
            features={
                'image': tf.FixedLenFeature([], tf.string),
                'label': tf.FixedLenFeature([], tf.int64)
            })
        image = tf.decode_raw(features['image'], tf.uint8)
        image.set_shape([DEPTH * HEIGHT * WIDTH])

        image = tf.cast(
            tf.transpose(tf.reshape(image, [DEPTH, HEIGHT, WIDTH]), [1, 2, 0]),
            tf.float32)
        label = tf.cast(features['label'], tf.int32)

        image = self.preprocess(image)
        return image, label

    def preprocess(self, image):
        """对train数据集进行扰乱，包括裁剪、亮度调整、对比度调整和翻转等操作"""
        if self.subset == 'train' and self.use_distortion:
            image = tf.image.resize_image_with_crop_or_pad(image, 40, 40)
            image = tf.random_crop(image, [HEIGHT, WIDTH, DEPTH]) # 裁剪
            image = tf.image.random_flip_left_right(image) # 左右翻转
            # image = tf.image.random_brightness(image, max_delta=10) # 亮度
            # image = tf.image.random_contrast(image, lower=0.2, upper=1.8) # 对比度
            # image = tf.image.random_hue(image, max_delta=0.1) # 色相
            # image = tf.image.random_flip_up_down(image) # 上下翻转
            # image = tf.image.random_saturation(image, 0, 5) # 饱和度
            # image = tf.image.random_jpeg_quality(image, 50, 90) # 噪声，jpeg质量
        return image

    def make_batch(self, batch_size):
        """通过TFRecordDataset读取文件，shuffle和batch数据集，返回一个batch的数据"""
        filenames = self.get_filenames()
        dataset = tf.data.TFRecordDataset(filenames).repeat()
        # num_parallel_calls并行处理，加速IO
        dataset = dataset.map(
            self.parser, num_parallel_calls=batch_size)
        # 缓冲池的大小设计
        if self.subset == 'train':
            min_queue_examples = int(
                Cifar10DataSet.num_examples_per_epoch(self.subset) * 0.4)
            dataset = dataset.shuffle(buffer_size=min_queue_examples + 3 * batch_size)

        dataset = dataset.batch(batch_size)
        iterator = dataset.make_one_shot_iterator()
        image_batch, label_batch = iterator.get_next()

        return image_batch, label_batch

    @staticmethod
    def num_examples_per_epoch(subset='train'):
        if subset == 'train':
            return 40000 # 对源码进行了修改
        elif subset == 'validation':
            return 10000
        elif subset == 'eval':
            return 10000
        else:
            raise ValueError('Invalid data subset "%s"' % subset)