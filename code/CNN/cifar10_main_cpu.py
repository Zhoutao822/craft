# Copyright
# License
# ==============================================================================
"""main
版本：
    TensorFlow：1.12
    Python：3.6.7

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
    'train_steps', 1000, 'Train steps.')
tf.app.flags.DEFINE_integer(
    'train_batch_size', 64, 'Train batch size.')
tf.app.flags.DEFINE_integer(
    'eval_batch_size', 64, 'Eval batch size.')    
tf.app.flags.DEFINE_integer(
    'num_layers', 44, 'The number of layers of the model.')
tf.app.flags.DEFINE_float(
    'momentum', 0.9, 'Momentum for MomentumOptimizer.')
tf.app.flags.DEFINE_float(
    'weight_decay', 2e-4, 'Weight decay for convolutions.')    
tf.app.flags.DEFINE_float(
    'learning_rate', 0.1, 'Learning rate value.') 
tf.app.flags.DEFINE_boolean(
    'use_distortion_for_training', True, 'If doing image distortion for training.') 
tf.app.flags.DEFINE_float(
    'batch_norm_decay', 0.997, 'Decay for batch norm.')   
tf.app.flags.DEFINE_float(
    'batch_norm_epsilon', 1e-5, 'Epsilon for batch norm.')   


def get_model_fn(num_workers):
    """"""

    def _resnet_model_fn(features, labels, mode, params):
        """
        
        
        Args:

        Returns:
            
        """
        is_training = (mode == tf.estimator.ModeKeys.TRAIN)
        weight_decay = params['weight_decay']
        momentum = params['momentum']

        with tf.variable_scope('resnet', reuse=False):
            with tf.name_scope('cpu') as name_scope:
                loss, grads, preds = _calc_fn(
                    is_training, weight_decay, features, labels,
                    params['num_layers'], params['batch_norm_decay'],
                    params['batch_norm_epsilon'])
                update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS, name_scope)
        
        num_batches_per_epoch = cifar10.Cifar10DataSet.num_examples_per_epoch(
            'train') // (params['train_batch_size'] * num_workers)
        boundaries = [
            num_batches_per_epoch * x
            for x in np.array([82, 123, 300], dtype=np.int64)
        ]
        staged_lr = [params['learning_rate'] * x for x in [1, 0.1, 0.01, 0.002]]

        learning_rate = tf.train.piecewise_constant(
            tf.train.get_global_step(), boundaries, staged_lr)

        loss = tf.identity(loss, name='loss')

        tensor_to_log = {'learning_rate': learning_rate, 'loss': loss}

        logging_hook = tf.train.LoggingTensorHook(
            tensors=tensor_to_log, every_n_iter=100)
        
        counter_hook = tf.train.StepCounterHook(every_n_steps=10)

        train_hooks = [logging_hook, counter_hook]

        optimizer = tf.train.MomentumOptimizer(
            learning_rate=learning_rate, momentum=momentum)

        train_op = [
            optimizer.apply_gradients(
                grads, global_step=tf.train.get_global_step())
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


def _calc_fn(is_training, weight_decay, feature, label, 
            num_layers, batch_norm_decay, batch_norm_epsilon):
    """
    
    Args:

    Returns:
    
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
    loss = tf.reduce_mean(loss)

    model_params = tf.trainable_variables()
    loss += weight_decay * tf.add_n([tf.nn.l2_loss(v) for v in model_params])
    grad = tf.gradients(loss, model_params)

    return loss, zip(grad, model_params), pred


def input_fn(data_dir,
            subset,
            batch_size,
            use_distortion_for_training=True):
    """
    
    Args:

    Returns:

    """
    use_distortion = subset == 'train' and use_distortion_for_training
    dataset = cifar10.Cifar10DataSet(data_dir, subset, use_distortion)
    image_batch, label_batch = dataset.make_batch(batch_size)
    return image_batch, label_batch


def main(flags):
    classifier = tf.estimator.Estimator(
        model_dir=flags.job_dir,
        model_fn=get_model_fn(1),
        params={
            'weight_decay': flags.weight_decay,
            'momentum': flags.momentum,
            'num_layers': flags.num_layers,
            'batch_norm_decay': flags.batch_norm_decay,
            'batch_norm_epsilon': flags.batch_norm_epsilon,
            'train_batch_size': flags.train_batch_size,
            'learning_rate': flags.learning_rate
        })
    classifier.train(input_fn=lambda: input_fn(
        flags.data_dir, 'train', flags.train_batch_size), 
        steps=flags.train_steps)
    classifier.evaluate(input_fn=lambda: input_fn(
        flags.data_dir, 'eval', flags.eval_batch_size))


if __name__ == '__main__':
    if not os.path.exists(FLAGS.data_dir):
        os.mkdir(FLAGS.data_dir)
    if not os.path.exists(FLAGS.job_dir):
        os.mkdir(FLAGS.job_dir)        
    main(FLAGS)    