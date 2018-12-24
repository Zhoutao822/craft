# Copyright
# License
# ==============================================================================
"""使用GPU进行训练的main文件，包括分布式，实际功能未测试
版本：
    TensorFlow：1.12
    Python：3.6.7
定义运行时参数，仅使用GPU进行训练和验证
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import itertools

import cifar10
import cifar10_model
import numpy as np
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.INFO)
FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string(
    'data_dir', './cifar10', 'Directory to generate tfrecords to.')
tf.app.flags.DEFINE_string(
    'job_dir', './tmp1', 'Directory to generate model to.')
tf.app.flags.DEFINE_string(
    'variable_strategy', 'CPU', 'Where to locate variable operations')
tf.app.flags.DEFINE_integer(
    'train_steps', 20000, 'Train steps.')
tf.app.flags.DEFINE_integer(
    'num_gpus', 0, 'The number of gpus used. Uses only CPU if set to 0.')
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
tf.app.flags.DEFINE_float(
    'weight_decay', 2e-4, 'Weight decay for convolutions.') 
tf.app.flags.DEFINE_integer(
    'decay_steps', 2000, 'The number of learning rate decay steps.')   
tf.app.flags.DEFINE_float(
    'decay_rate', 0.96, 'Decay rate value.')   
tf.app.flags.DEFINE_string(
    'data_format', None, """If not set, the data format best for the training device is used. 
    Allowed values: channels_first (NCHW) channels_last (NHWC).""")
tf.app.flags.DEFINE_boolean(
    'log_device_placement', False, 'Whether to log device placement.') 
tf.app.flags.DEFINE_boolean(
    'sync', False, 'If present when running in a distributed environment will run on sync mode.') 
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


def get_model_fn(num_gpus, variable_strategy, num_workers):
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
        weight_decay = params['weight_decay']
        # 多GPU需要分别计算不同设备的loss和梯度，再综合起来
        tower_features = features
        tower_labels = labels
        tower_losses = []
        tower_gradvars = []
        tower_preds = []

        data_format = params['data_format']
        if not data_format:
            if num_gpus == 0:
                data_format = 'channels_last'
            else:
                data_format = 'channels_first'

        if num_gpus == 0:
            num_devices = 1
            device_type = 'cpu'
        else:
            num_devices = num_gpus
            device_type = 'gpu'
        # Todo GPU部分代码没有测试，不知道是不是对的
        for i in range(num_devices):
            worker_device = '/{}:{}'.format(device_type, i)
            if variable_strategy == 'CPU':
                device_setter = tf.train.replica_device_setter(
                    worker_device=worker_device)
            elif variable_strategy == 'GPU':
                device_setter = tf.train.replica_device_setter(
                    worker_device=worker_device,
                    ps_strategy=tf.contrib.training.GreedyLoadBalancingStrategy(
                        num_gpus, tf.contrib.training.byte_size_load_fn))
            with tf.variable_scope('resnet', reuse=bool(i != 0)):
                with tf.name_scope('tower_%d' % i) as name_scope:
                    with tf.device(device_setter):
                        loss, gradvars, preds = _calc_fn(
                            is_training, weight_decay, tower_features[i], 
                            tower_labels[i], data_format, params['num_layers'], 
                            params['batch_norm_decay'], params['batch_norm_epsilon'])
                        tower_losses.append(loss)
                        tower_gradvars.append(gradvars)
                        tower_preds.append(preds)
                        if i == 0:
                            # batch_norm需要更新
                            update_ops = tf.get_collection(
                                tf.GraphKeys.UPDATE_OPS, name_scope)
        
        gradvars = []
        with tf.name_scope('gradient_averaging'):
            all_grads = {}
            for grad, var in itertools.chain(*tower_gradvars):
                if grad is not None:
                    all_grads.setdefault(var, []).append(grad)
            for var, grads in all_grads.items():
                with tf.device(var.device):
                    if len(grads) == 1:
                        avg_grad = grads[0]
                    else:
                        avg_grad = tf.multiply(tf.add_n(grads), 1. / len(grads))
                gradvars.append((avg_grad, var))

        consolidation_device = '/gpu:0' if variable_strategy == 'GPU' else '/cpu:0'
        with tf.device(consolidation_device):
            # 使用tf.train.exponential_decay实现学习率衰减
            learning_rate = tf.train.exponential_decay(
                learning_rate=learning_rate,
                global_step=tf.train.get_global_step(),
                decay_steps=decay_steps,
                decay_rate=decay_rate
            )
            loss = tf.reduce_mean(tower_losses, name='loss')

            # tensor_to_log是dict类型，且key为tensor的name
            tensor_to_log = {'learning_rate': learning_rate, 'loss': loss}
            logging_hook = tf.train.LoggingTensorHook(
                tensors=tensor_to_log, every_n_iter=100)
        
            counter_hook = tf.train.StepCounterHook(every_n_steps=20)

            train_hooks = [logging_hook, counter_hook]

            optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
            # Todo，分布式代码没有测试
            if params['sync']:
                optimizer = tf.train.SyncReplicasOptimizer(
                    optimizer, replicas_to_aggregate=num_workers)
                sync_replicas_hook = optimizer.make_session_run_hook(params['is_chief'])
                train_hooks.append(sync_replicas_hook)
            train_op = [
                optimizer.apply_gradients(
                    gradvars, global_step=tf.train.get_global_step())
            ]
            train_op.extend(update_ops)
            train_op = tf.group(*train_op)

            predictions = {
                'classes': 
                    tf.concat([p['classes'] for p in tower_preds], axis=0),
                'probabilities': 
                    tf.concat([p['probabilities'] for p in tower_preds], axis=0)
            }
            stacked_labels = tf.concat(labels, axis=0)

            metrics = {
                'accuracy':
                    tf.metrics.accuracy(stacked_labels, predictions['classes'])
            }
        return tf.estimator.EstimatorSpec(
            mode=mode,
            predictions=predictions,
            loss=loss,
            train_op=train_op,
            training_hooks=train_hooks,
            eval_metric_ops=metrics)

    return _resnet_model_fn


def _calc_fn(is_training, weight_decay, feature, label, data_format,
            num_layers, batch_norm_decay, batch_norm_epsilon):
    """
    获取model，简单计算
    Args:
        is_training：判断是train还是evaluate
        weight_decay：l2损失系数
        feature：一个batch的image数据
        label：一个batch的label数据
        data_format：channels_last (NHWC) or channels_first (NCHW)
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
        data_format=data_format)
    logits = model.forward_pass(feature, input_data_format='channels_last')
    pred = {
        'classes': tf.argmax(input=logits, axis=1),
        'probabilities': tf.nn.softmax(logits)
    }

    loss = tf.losses.sparse_softmax_cross_entropy(
        logits=logits, labels=label)
    loss = tf.reduce_mean(loss)

    model_params = tf.trainable_variables()
    loss += weight_decay * tf.add_n([tf.nn.l2_loss(v) for v in model_params])
    grad = tf.gradients(loss, model_params)
    return loss, zip(grad, model_params), pred


def input_fn(data_dir,
            subset,
            num_shards,
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
    with tf.device('/cpu:0'):
        use_distortion = subset == 'train' and use_distortion_for_training
        dataset = cifar10.Cifar10DataSet(data_dir, subset, use_distortion)
        image_batch, label_batch = dataset.make_batch(batch_size)
        if num_shards <= 1:
            return [image_batch], [label_batch] # 必须返回list，对应_calc_fn的参数
        # 均分训练数据给不同的设备
        image_batch = tf.unstack(image_batch, num=batch_size, axis=0)
        label_batch = tf.unstack(label_batch, num=batch_size, axis=0)
        feature_shards = [[] for i in range(num_shards)]
        label_shards = [[] for i in range(num_shards)]
        for i in range(batch_size):
            idx = i % num_shards
            feature_shards[idx].append(image_batch[i])
            label_shards[idx].append(label_batch[i])
        feature_shards = [tf.parallel_stack(x) for x in feature_shards]
        label_shards = [tf.parallel_stack(x) for x in label_shards]
        return feature_shards, label_shards

def main(flags):
    # The env variable is on deprecation path, default is set to off.
    os.environ['TF_SYNC_ON_FINISH'] = '0'
    os.environ['TF_ENABLE_WINOGRAD_NONFUSED'] = '1'
    # 为了调用多线程运行，需要使用tf.ConfigProto，
    # device_count指定最多使用多少devices，比如CPU，最多仅支持1；
    # 如果有多个GPU，可以指定最多使用其中的多少个，键值对形式
    # intra_op_parallelism_threads 控制运算符op内部的并行
    # inter_op_parallelism_threads 控制多个运算符op之间的并行计算
    run_config = tf.ConfigProto(
        device_count={"CPU": 1, "GPU": 0},
        allow_soft_placement=True, # GPU显存相关，自动增加
        log_device_placement=flags.log_device_placement,
        gpu_options=tf.GPUOptions(force_gpu_compatible=True),
        intra_op_parallelism_threads=flags.num_intra_threads,
        inter_op_parallelism_threads=flags.num_inter_threads)
    # tf.ConfigProto不能直接添加到Estimator中，
    # 需要使用tf.estimator.RunConfig包裹一下，顺便指定模型存储路径model_dir
    config = tf.estimator.RunConfig(
        model_dir=flags.job_dir,
        session_config=run_config)
    # tf.estimator.Estimator的params必须是dict类型
    classifier = tf.estimator.Estimator(
        model_fn=get_model_fn(
            flags.num_gpus, 
            flags.variable_strategy, 
            config.num_worker_replicas or 1),
        config=config,
        params={
            'decay_steps': flags.decay_steps,
            'decay_rate': flags.decay_rate,
            'num_layers': flags.num_layers,
            'weight_decay': flags.weight_decay,
            'batch_norm_decay': flags.batch_norm_decay,
            'batch_norm_epsilon': flags.batch_norm_epsilon,
            'train_batch_size': flags.train_batch_size,
            'learning_rate': flags.learning_rate,
            'data_format': flags.data_format,
            'sync': flags.sync,
            'is_chief':config.is_chief
        })
    # 循环多次以观察eval的变化，防止过拟合
    for _ in range(3):
        classifier.train(input_fn=lambda: input_fn(
            flags.data_dir, 'train', flags.num_gpus, flags.train_batch_size), 
            steps=flags.train_steps)
        classifier.evaluate(input_fn=lambda: input_fn(
            flags.data_dir, 'eval', flags.num_gpus, flags.eval_batch_size),
            steps=flags.eval_steps)


if __name__ == '__main__':
    if not os.path.exists(FLAGS.data_dir):
        os.mkdir(FLAGS.data_dir)
    if not os.path.exists(FLAGS.job_dir):
        os.mkdir(FLAGS.job_dir)      
    # 下面是对参数的一些约束，比如使用GPU数量与ResNet网络层数的逻辑约束等
    if FLAGS.num_gpus > 0:
        assert tf.test.is_gpu_available(), 'Requested GPUs but none found.'
    if FLAGS.num_gpus < 0:
        raise ValueError(
        'Invalid GPU count: \"--num-gpus\" must be 0 or a positive integer.')
    if FLAGS.num_gpus == 0 and FLAGS.variable_strategy == 'GPU':
        raise ValueError('num-gpus=0, CPU must be used as parameter server. Set'
                     '--variable-strategy=CPU.')
    if (FLAGS.num_layers - 2) % 6 != 0:
        raise ValueError('Invalid --num-layers parameter.')
    if FLAGS.num_gpus != 0 and FLAGS.train_batch_size % FLAGS.num_gpus != 0:
        raise ValueError('--train-batch-size must be multiple of --num-gpus.')
    if FLAGS.num_gpus != 0 and FLAGS.eval_batch_size % FLAGS.num_gpus != 0:
        raise ValueError('--eval-batch-size must be multiple of --num-gpus.')
    if cifar10.Cifar10DataSet.num_examples_per_epoch('eval') % FLAGS.eval_batch_size != 0:
        raise ValueError('validation set size must be multiple of eval_batch_size')

    tf.app.run(main(FLAGS))   