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

import cifar10
import cifar10_model
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
tf.app.flags.DEFINE_integer(
    'decay_steps', 2000, 'The number of learning rate decay steps.')   
tf.app.flags.DEFINE_float(
    'decay_rate', 0.96, 'Decay rate value.')   
tf.app.flags.DEFINE_boolean(
    'use_distortion_for_training', True, 'If doing image distortion for training.') 
tf.app.flags.DEFINE_float(
    'batch_norm_decay', 0.997, 'Decay for batch norm.')   
tf.app.flags.DEFINE_float(
    'batch_norm_epsilon', 1e-5, 'Epsilon for batch norm.')   
tf.app.flags.DEFINE_integer(
    'num_inter_threads', 6, 'Number of threads to use for inter-op parallelism.')
tf.app.flags.DEFINE_integer(
    'num_intra_threads', 6, 'Number of threads to use for intra-op parallelism.')


def get_model_fn():
    """返回Estimator的model_fn"""

    def _resnet_model_fn(features, labels, mode, params):
        """
        返回包含Resnet模型的EstimatorSpec，只有train和evaluate方法，
        没有predict方法，优化器使用Adam，learning rate会自动衰减
        
        Args:
            features：一个batch的image数据
            labels：一个batch的label数据
            mode：调用train还是evaluate
            params：其他运行参数
        Returns:
            tf.estimator.EstimatorSpec
        """
        is_training = (mode == tf.estimator.ModeKeys.TRAIN)
        decay_steps = params['decay_steps'] # 学习率衰减的steps
        decay_rate = params['decay_rate'] # 学习率衰减率
        learning_rate = params['learning_rate']

        loss, preds = _calc_fn(
            is_training, features, labels,
            params['num_layers'], params['batch_norm_decay'],
            params['batch_norm_epsilon'])
        # batch_norm需要更新
        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        
        # 使用tf.train.exponential_decay实现学习率衰减
        learning_rate = tf.train.exponential_decay(
            learning_rate=learning_rate,
            global_step=tf.train.get_global_step(),
            decay_steps=decay_steps,
            decay_rate=decay_rate
        )

        # tensor_to_log是dict类型，且key为tensor的name
        avg_loss = tf.reduce_mean(loss)
        avg_loss = tf.identity(avg_loss, name='loss')
        tensor_to_log = {'learning_rate': learning_rate, 'loss': avg_loss}
        logging_hook = tf.train.LoggingTensorHook(
            tensors=tensor_to_log, every_n_iter=100)
        
        counter_hook = tf.train.StepCounterHook(every_n_steps=20)

        train_hooks = [logging_hook, counter_hook]

        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)

        train_op = [
            optimizer.minimize(
                loss, global_step=tf.train.get_global_step())
        ]
        train_op.extend(update_ops)
        train_op = tf.group(*train_op)

        predictions = {
            'classes': preds['classes'],
            'probabilities': preds['probabilities']
        }
        metrics = {
            'accuracy':
                tf.metrics.accuracy(labels, predictions['classes'])
        }
        return tf.estimator.EstimatorSpec(
            mode=mode,
            predictions=predictions,
            loss=loss,
            train_op=train_op,
            training_hooks=train_hooks,
            eval_metric_ops=metrics)

    return _resnet_model_fn


def _calc_fn(is_training, feature, label, 
            num_layers, batch_norm_decay, batch_norm_epsilon):
    """
    获取model，简单计算
    Args:
        is_training：判断是train还是evaluate
        feature：一个batch的image数据
        label：一个batch的label数据
        num_layers：Resnet层数
        batch_norm_decay：Resnet参数
        batch_norm_epsilon：Resnet参数
    Returns:
        loss：一个batch的softmax_cross_entropy
        pred：字典类型包括一个batch的标签和概率
    """
    model = cifar10_model.ResNetCifar10(
        num_layers,
        batch_norm_decay=batch_norm_decay,
        batch_norm_epsilon=batch_norm_epsilon,
        is_training=is_training,
        data_format='channels_last')
    logits = model.forward_pass(feature, input_data_format='channels_last')
    pred = {
        'classes': tf.argmax(input=logits, axis=1),
        'probabilities': tf.nn.softmax(logits)
    }

    loss = tf.losses.sparse_softmax_cross_entropy(
        logits=logits, labels=label)
    return loss, pred


def input_fn(data_dir,
            subset,
            batch_size,
            use_distortion_for_training=True):
    """
    输入函数，可以用于train数据集合eval数据集
    Args:
        data_dir：tfrecords文件所在的文件夹
        subset：判断是train还是evaluate
        batch_size：一个batch的大小
        use_distortion_for_training：是否对数据进行扰动
    Returns:
        image_batch：一个batch的image数据
        label_batch：一个batch的label数据
    """
    use_distortion = subset == 'train' and use_distortion_for_training
    dataset = cifar10.Cifar10DataSet(data_dir, subset, use_distortion)
    image_batch, label_batch = dataset.make_batch(batch_size)
    return image_batch, label_batch


def main(flags):
    # 为了调用多线程运行，需要使用tf.ConfigProto，
    # device_count指定最多使用多少devices，比如CPU，最多仅支持1；
    # 如果有多个GPU，可以指定最多使用其中的多少个，键值对形式
    # intra_op_parallelism_threads 控制运算符op内部的并行
    # inter_op_parallelism_threads 控制多个运算符op之间的并行计算
    run_config = tf.ConfigProto(
        device_count={"CPU": 1},
        intra_op_parallelism_threads=flags.num_intra_threads,
        inter_op_parallelism_threads=flags.num_inter_threads)
    # tf.ConfigProto不能直接添加到Estimator中，
    # 需要使用tf.estimator.RunConfig包裹一下，顺便指定模型存储路径model_dir
    config = tf.estimator.RunConfig(
        model_dir=flags.job_dir,
        session_config=run_config)
    # tf.estimator.Estimator的params必须是dict类型
    classifier = tf.estimator.Estimator(
        model_fn=get_model_fn(),
        config=config,
        params={
            'decay_steps': flags.decay_steps,
            'decay_rate': flags.decay_rate,
            'num_layers': flags.num_layers,
            'batch_norm_decay': flags.batch_norm_decay,
            'batch_norm_epsilon': flags.batch_norm_epsilon,
            'train_batch_size': flags.train_batch_size,
            'learning_rate': flags.learning_rate
        })
    # 循环多次以观察eval的变化，防止过拟合
    for _ in range(50):
        classifier.train(input_fn=lambda: input_fn(
            flags.data_dir, 'train', flags.train_batch_size), 
            steps=flags.train_steps)
        classifier.evaluate(input_fn=lambda: input_fn(
            flags.data_dir, 'eval', flags.eval_batch_size),
            steps=flags.eval_steps)


if __name__ == '__main__':
    if not os.path.exists(FLAGS.data_dir):
        os.mkdir(FLAGS.data_dir)
    if not os.path.exists(FLAGS.job_dir):
        os.mkdir(FLAGS.job_dir)        
    tf.app.run(main(FLAGS))  