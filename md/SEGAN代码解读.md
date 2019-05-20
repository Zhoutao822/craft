[SEGAN-GitHub](https://github.com/santi-pdp/segan)

[SEGAN-Paper](https://arxiv.org/abs/1703.09452)

[Samples](http://veu.talp.cat/segan/)

## ops.py

ops.py保存一些常用的函数

```python
from __future__ import print_function
import tensorflow as tf
from tensorflow.contrib.layers import batch_norm, fully_connected, flatten
from tensorflow.contrib.layers import xavier_initializer
from contextlib import contextmanager # 管理上下文
import numpy as np


def gaussian_noise_layer(input_layer, std):
    """给input_layer增加高斯噪声
    
    Args:
        input_layer ([type]): 目标layer
        std ([type]): 高斯噪声的标准差
    """
    noise = tf.random_normal(
        shape=input_layer.get_shape().as_list(),
        mean=0.0,
        stddev=std,
        dtype=tf.float32)
    return input_layer + noise


def sample_random_walk(batch_size, dim):
    """生成一个 batch_size * dim 的二维随机数组，每一行的均值为0，标准差为1
    当dim=2时，仅有1和-1
    
    Args:
        batch_size ([type]): [description]
        dim ([type]): [description]
    """
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


def scalar_summary(name, x):
    """用来显示标量信息
    
    Args:
        name ([type]): tag标签
        x ([type]): 需要显示的值，比如loss和accuracy
    """
    try:
        summ = tf.summary.scalar(name, x)
    except AttributeError:
        summ = tf.summary.scalar(name, x)
    return summ


def histogram_summary(name, x):
    """用来显示直方图信息
    
    Args:
        name ([type]): tag标签
        x ([type]): 一般用来显示训练过程中变量的分布情况
    """
    try:
        summ = tf.summary.histogram(name, x)
    except AttributeError:
        summ = tf.summary.histogram(name, x)
    return summ


def tensor_summary(name, x):
    """用来显示张量信息
    
    Args:
        name ([type]): tag标签
        x ([type]): 训练过程中的张量
    """
    try:
        summ = tf.summary.tensor_summary(name, x)
    except AttributeError:
        summ = tf.summary.tensor_summary(name, x)
    return summ


def audio_summary(name, x, sampling_rate=16e3):
    """展示训练过程中记录的音频 
    
    Args:
        name ([type]): tag标签
        x ([type]): audio从tensor生成，此tensor只能为3-D([batch_size, frames, channels])或2-D([batch_size, frames])，值大小在[-1.0, 1.0]
        sampling_rate (float32): 音频采样率. Defaults to 16e3.
    """
    try:
        summ = tf.summary.audio(name, x, sampling_rate)
    except AttributeError:
        summ = tf.summary.audio(name, x, sampling_rate)
    return summ


def minmax_normalize(x, x_min, x_max, o_min=-1., o_max=1.):
    """minmax归一化，约束到[-1.0, 1.0]
    
    Args:
        x ([type]): [description]
        x_min ([type]): [description]
        x_max ([type]): [description]
        o_min ([type], optional): [description]. Defaults to -1..
        o_max ([type], optional): [description]. Defaults to 1..
    """
    return (o_max - o_min) / (x_max - x_min) * (x - x_max) + o_max


def minmax_denormalize(x, x_min, x_max, o_min=-1., o_max=1.):
    """反归一化，还原数据
    
    Args:
        x ([type]): [description]
        x_min ([type]): [description]
        x_max ([type]): [description]
        o_min ([type], optional): [description]. Defaults to -1..
        o_max ([type], optional): [description]. Defaults to 1..
    """
    return minmax_normalize(x, o_min, o_max, x_min, x_max)


def downconv(x,
             output_dim,
             kwidth=5,
             pool=2,
             init=None,
             uniform=False,
             bias_init=None,
             name='downconv'):
    """ Downsampled convolution 1d """
    x2d = tf.expand_dims(x, 2) # 给x增加一个维度，根据上下文可知x2d有4个维度
    w_init = init # 初始化函数
    if w_init is None:
        w_init = xavier_initializer(uniform=uniform)
    with tf.variable_scope(name):
        # W为卷积核参数，他的形状是[卷积核的高度，卷积核的宽度，图像通道数，卷积核个数]，要求类型与参数input相同，有一个地方需要注意，第三维in_channels，就是参数input的第四维
        W = tf.get_variable(
            'W', [kwidth, 1, x.get_shape()[-1], output_dim],
            initializer=w_init)
        conv = tf.nn.conv2d(x2d, W, strides=[1, pool, 1, 1], padding='SAME')
        if bias_init is not None:
            b = tf.get_variable('b', [output_dim], initializer=bias_init)
            conv = tf.reshape(tf.nn.bias_add(conv, b), conv.get_shape())
        else:
            conv = tf.reshape(conv, conv.get_shape())
        # reshape back to 1d
        # 这里仅取shape的前两维度与最后一个维度的和
        conv = tf.reshape(
            conv,
            conv.get_shape().as_list()[:2] + [conv.get_shape().as_list()[-1]])
        return conv


# https://github.com/carpedm20/lstm-char-cnn-tensorflow/blob/master/models/ops.py
def highway(input_, size, layer_size=1, bias=-2, f=tf.nn.relu, name='hw'):
    """Highway Network (cf. http://arxiv.org/abs/1505.00387).
    t = sigmoid(Wy + b)
    z = t * g(Wy + b) + (1 - t) * y
    where g is nonlinearity, t is transform gate, and (1 - t) is carry gate.
    类似于ResNet的残差
    """
    output = input_
    for idx in range(layer_size):
        lin_scope = '{}_output_lin_{}'.format(name, idx)
        output = f(tf.contrib.rnn._linear(output, size, 0, scope=lin_scope))
        transform_scope = '{}_transform_lin_{}'.format(name, idx)
        transform_gate = tf.sigmoid(
            tf.contrib.rnn._linear(input_, size, 0, scope=transform_scope) +
            bias)
        carry_gate = 1. - transform_gate

        output = transform_gate * output + carry_gate * input_

    return output


def leakyrelu(x, alpha=0.3, name='lrelu'):
    # tf.nn.leaky_relu替换
    return tf.maximum(x, alpha * x, name=name)


def prelu(x, name='prelu', ref=False):
    in_shape = x.get_shape().as_list()
    with tf.variable_scope(name):
        # make one alpha per feature
        alpha = tf.get_variable(
            'alpha',
            in_shape[-1],
            initializer=tf.constant_initializer(0.),
            dtype=tf.float32)
        pos = tf.nn.relu(x)
        neg = alpha * (x - tf.abs(x)) * .5
        if ref:
            # return ref to alpha vector
            return pos + neg, alpha
        else:
            return pos + neg


def conv1d(x,
           kwidth=5,
           num_kernels=1,
           init=None,
           uniform=False,
           bias_init=None,
           name='conv1d',
           padding='SAME'):
    # 一维卷积
    input_shape = x.get_shape()
    in_channels = input_shape[-1]
    assert len(input_shape) >= 3
    w_init = init
    if w_init is None:
        w_init = xavier_initializer(uniform=uniform)
    with tf.variable_scope(name):
        # filter shape: [kwidth, in_channels, num_kernels]
        W = tf.get_variable(
            'W', [kwidth, in_channels, num_kernels], initializer=w_init)
        conv = tf.nn.conv1d(x, W, stride=1, padding=padding)
        if bias_init is not None:
            b = tf.get_variable(
                'b', [num_kernels],
                initializer=tf.constant_initializer(bias_init))
            conv = conv + b
        return conv


def time_to_batch(value, dilation, name=None):
    with tf.name_scope('time_to_batch'):
        shape = tf.shape(value)
        pad_elements = dilation - 1 - (shape[1] + dilation - 1) % dilation
        padded = tf.pad(value, [[0, 0], [0, pad_elements], [0, 0]])
        reshaped = tf.reshape(padded, [-1, dilation, shape[2]])
        transposed = tf.transpose(reshaped, perm=[1, 0, 2])
        return tf.reshape(transposed, [shape[0] * dilation, -1, shape[2]])


# https://github.com/ibab/tensorflow-wavenet/blob/master/wavenet/ops.py
def batch_to_time(value, dilation, name=None):
    with tf.name_scope('batch_to_time'):
        shape = tf.shape(value)
        prepared = tf.reshape(value, [dilation, -1, shape[2]])
        transposed = tf.transpose(prepared, perm=[1, 0, 2])
        return tf.reshape(transposed,
                          [tf.div(shape[0], dilation), -1, shape[2]])


def atrous_conv1d(value,
                  dilation,
                  kwidth=3,
                  num_kernels=1,
                  name='atrous_conv1d',
                  bias_init=None,
                  stddev=0.02):
    # 空洞卷积
    # dilation rate 指的是kernel的间隔数量(e.g. 正常的 convolution 是 dilatation rate 1)
    # tf.layers.conv1d替换
    input_shape = value.get_shape().as_list()
    in_channels = input_shape[-1]
    assert len(input_shape) >= 3
    with tf.variable_scope(name):
        weights_init = tf.truncated_normal_initializer(stddev=0.02)
        # filter shape: [kwidth, in_channels, output_channels]
        filter_ = tf.get_variable(
            'w',
            [kwidth, in_channels, num_kernels],
            initializer=weights_init,
        )
        padding = [[0, 0], [(kwidth / 2) * dilation, (kwidth / 2) * dilation],
                   [0, 0]]
        padded = tf.pad(value, padding, mode='SYMMETRIC')
        if dilation > 1:
            transformed = time_to_batch(padded, dilation)
            conv = tf.nn.conv1d(transformed, filter_, stride=1, padding='SAME')
            restored = batch_to_time(conv, dilation)
        else:
            restored = tf.nn.conv1d(padded, filter_, stride=1, padding='SAME')
        # Remove excess elements at the end.
        result = tf.slice(restored, [0, 0, 0],
                          [-1, input_shape[1], num_kernels])
        if bias_init is not None:
            b = tf.get_variable(
                'b', [num_kernels],
                initializer=tf.constant_initializer(bias_init))
            result = tf.add(result, b)
        return result


def residual_block(input_,
                   dilation,
                   kwidth,
                   num_kernels=1,
                   bias_init=None,
                   stddev=0.02,
                   do_skip=True,
                   name='residual_block'):
    # 残差网络
    print('input shape to residual block: ', input_.get_shape())
    with tf.variable_scope(name):
        h_a = atrous_conv1d(
            input_,
            dilation,
            kwidth,
            num_kernels,
            bias_init=bias_init,
            stddev=stddev)
        h = tf.tanh(h_a)
        # apply gated activation
        z_a = atrous_conv1d(
            input_,
            dilation,
            kwidth,
            num_kernels,
            name='conv_gate',
            bias_init=bias_init,
            stddev=stddev)
        z = tf.nn.sigmoid(z_a)
        print('gate shape: ', z.get_shape())
        # element-wise apply the gate
        gated_h = tf.multiply(z, h)
        print('gated h shape: ', gated_h.get_shape())
        #make res connection
        h_ = conv1d(
            gated_h,
            kwidth=1,
            num_kernels=1,
            init=tf.truncated_normal_initializer(stddev=stddev),
            name='residual_conv1')
        res = h_ + input_
        print('residual result: ', res.get_shape())
        if do_skip:
            #make skip connection
            skip = conv1d(
                gated_h,
                kwidth=1,
                num_kernels=1,
                init=tf.truncated_normal_initializer(stddev=stddev),
                name='skip_conv1')
            return res, skip
        else:
            return res


# Code from keras backend
# tf.keras.backend.repeat_elements
# https://github.com/fchollet/keras/blob/master/keras/backend/tensorflow_backend.py
def repeat_elements(x, rep, axis):
    """Repeats the elements of a tensor along an axis, like `np.repeat`.
    If `x` has shape `(s1, s2, s3)` and `axis` is `1`, the output
    will have shape `(s1, s2 * rep, s3)`.
    # Arguments
        x: Tensor or variable.
        rep: Python integer, number of times to repeat.
        axis: Axis along which to repeat.
    # Raises
        ValueError: In case `x.shape[axis]` is undefined.
    # Returns
        A tensor.
    """
    x_shape = x.get_shape().as_list()
    if x_shape[axis] is None:
        raise ValueError('Axis ' + str(axis) + ' of input tensor '
                         'should have a defined dimension, but is None. '
                         'Full tensor shape: ' + str(tuple(x_shape)) + '. '
                         'Typically you need to pass a fully-defined '
                         '`input_shape` argument to your first layer.')
    # slices along the repeat axis
    splits = tf.split(split_dim=axis, num_split=x_shape[axis], value=x)
    # repeat each slice the given number of reps
    x_rep = [s for s in splits for _ in range(rep)]
    return tf.concat(axis, x_rep)


def nn_deconv(x,
              kwidth=5,
              dilation=2,
              init=None,
              uniform=False,
              bias_init=None,
              name='nn_deconv1d'):
    # first compute nearest neighbour interpolated x 最近邻居插值
    interp_x = repeat_elements(x, dilation, 1)
    # run a convolution over the interpolated fmap
    dec = conv1d(
        interp_x,
        kwidth=5,
        num_kernels=1,
        init=init,
        uniform=uniform,
        bias_init=bias_init,
        name=name,
        padding='SAME')
    return dec


def deconv(x,
           output_shape,
           kwidth=5,
           dilation=2,
           init=None,
           uniform=False,
           bias_init=None,
           name='deconv1d'):
    # 反卷积
    input_shape = x.get_shape()
    in_channels = input_shape[-1]
    out_channels = output_shape[-1]
    assert len(input_shape) >= 3
    # reshape the tensor to use 2d operators
    x2d = tf.expand_dims(x, 2)
    o2d = output_shape[:2] + [1] + [output_shape[-1]]
    w_init = init
    if w_init is None:
        w_init = xavier_initializer(uniform=uniform)
    with tf.variable_scope(name):
        # filter shape: [kwidth, output_channels, in_channels]
        W = tf.get_variable(
            'W', [kwidth, 1, out_channels, in_channels], initializer=w_init)
        try:
            deconv = tf.nn.conv2d_transpose(
                x2d, W, output_shape=o2d, strides=[1, dilation, 1, 1])
        except AttributeError:
            # support for versions of TF before 0.7.0
            # based on https://github.com/carpedm20/DCGAN-tensorflow
            deconv = tf.nn.conv2d_transpose(
                x2d, W, output_shape=o2d, strides=[1, dilation, 1, 1])
        if bias_init is not None:
            b = tf.get_variable(
                'b', [out_channels], initializer=tf.constant_initializer(0.))
            deconv = tf.reshape(tf.nn.bias_add(deconv, b), deconv.get_shape())
        else:
            deconv = tf.reshape(deconv, deconv.get_shape())
        # reshape back to 1d
        deconv = tf.reshape(deconv, output_shape)
        return deconv


def conv2d(input_,
           output_dim,
           k_h,
           k_w,
           stddev=0.05,
           name="conv2d",
           with_w=False):
    with tf.variable_scope(name):
        w = tf.get_variable(
            'w', [k_h, k_w, input_.get_shape()[-1], output_dim],
            initializer=tf.truncated_normal_initializer(stddev=stddev))
        conv = tf.nn.conv2d(input_, w, strides=[1, 1, 1, 1], padding='VALID')
        if with_w:
            return conv, w
        else:
            return conv


# https://github.com/openai/improved-gan/blob/master/imagenet/ops.py
@contextmanager
def variables_on_gpu0():
    old_fn = tf.get_variable

    def new_fn(*args, **kwargs):
        with tf.device("/gpu:0"):
            return old_fn(*args, **kwargs)

    tf.get_variable = new_fn
    yield
    tf.get_variable = old_fn


def average_gradients(tower_grads):
    """ Calculate the average gradient for each shared variable across towers.

    Note that this function provides a sync point across al towers.
    Args:
        tower_grads: List of lists of (gradient, variable) tuples. The outer
        list is over individual gradients. The inner list is over the gradient
        calculation for each tower.
    Returns:
        List of pairs of (gradient, variable) where the gradient has been
        averaged across all towers.
    """

    average_grads = []
    for grad_and_vars in zip(*tower_grads):
        # each grad is ((grad0_gpu0, var0_gpu0), ..., (grad0_gpuN, var0_gpuN))
        grads = []
        for g, _ in grad_and_vars:
            # Add 0 dim to gradients to represent tower
            expanded_g = tf.expand_dims(g, 0)

            # Append on a 'tower' dimension that we will average over below
            grads.append(expanded_g)

        # Build the tensor and average along tower dimension
        grad = tf.concat(grads, 0)
        grad = tf.reduce_mean(grad, 0)

        # The Variables are redundant because they are shared across towers
        # just return first tower's pointer to the Variable
        v = grad_and_vars[0][1]
        grad_and_var = (grad, v)
        average_grads.append(grad_and_var)
    return average_grads

```

## data_loader.py

读取数据，数据增强与还原

```python
from __future__ import print_function
import tensorflow as tf
from ops import *
import numpy as np


def pre_emph(x, coeff=0.95):
    x0 = tf.reshape(x[0], [
        1,
    ])
    diff = x[1:] - coeff * x[:-1]
    concat = tf.concat([x0, diff], 0)
    return concat


def de_emph(y, coeff=0.95):
    if coeff <= 0:
        return y
    x = np.zeros(y.shape[0], dtype=np.float32)
    x[0] = y[0]
    for n in range(1, y.shape[0], 1):
        x[n] = coeff * x[n - 1] + y[n]
    return x


def read_and_decode(filename_queue, canvas_size, preemph=0.):
    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(filename_queue)
    features = tf.parse_single_example(
        serialized_example,
        features={
            'wav_raw': tf.FixedLenFeature([], tf.string),
            'noisy_raw': tf.FixedLenFeature([], tf.string),
        })
    wave = tf.decode_raw(features['wav_raw'], tf.int32)
    wave.set_shape(canvas_size)
    # 归一化
    wave = (2. / 65535.) * tf.cast((wave - 32767), tf.float32) + 1.
    noisy = tf.decode_raw(features['noisy_raw'], tf.int32)
    noisy.set_shape(canvas_size)
    noisy = (2. / 65535.) * tf.cast((noisy - 32767), tf.float32) + 1.

    if preemph > 0:
        wave = tf.cast(pre_emph(wave, preemph), tf.float32)
        noisy = tf.cast(pre_emph(noisy, preemph), tf.float32)

    return wave, noisy
```

## bnorm.py

```python
import tensorflow as tf

class VBN(object):
    """
    Virtual Batch Normalization
    (modified from https://github.com/openai/improved-gan/ definition)
    """

    def __init__(self, x, name, epsilon=1e-5):
        """
        x is the reference batch
        """
        assert isinstance(epsilon, float)

        shape = x.get_shape().as_list()
        assert len(shape) == 3, shape
        with tf.variable_scope(name) as scope:
            assert name.startswith("d_") or name.startswith("g_")
            self.epsilon = epsilon
            self.name = name
            self.mean = tf.reduce_mean(x, [0, 1], keep_dims=True)
            self.mean_sq = tf.reduce_mean(tf.square(x), [0, 1], keep_dims=True)
            self.batch_size = int(x.get_shape()[0])
            assert x is not None
            assert self.mean is not None
            assert self.mean_sq is not None
            out = self._normalize(x, self.mean, self.mean_sq, "reference")
            self.reference_output = out

    def __call__(self, x):

        shape = x.get_shape().as_list()
        with tf.variable_scope(self.name) as scope:
            new_coeff = 1. / (self.batch_size + 1.)
            old_coeff = 1. - new_coeff
            new_mean = tf.reduce_mean(x, [0, 1], keep_dims=True)
            new_mean_sq = tf.reduce_mean(tf.square(x), [0, 1], keep_dims=True)
            mean = new_coeff * new_mean + old_coeff * self.mean
            mean_sq = new_coeff * new_mean_sq + old_coeff * self.mean_sq
            out = self._normalize(x, mean, mean_sq, "live")
            return out

    def _normalize(self, x, mean, mean_sq, message):
        # make sure this is called with a variable scope
        shape = x.get_shape().as_list()
        assert len(shape) == 3
        self.gamma = tf.get_variable("gamma", [shape[-1]],
                                initializer=tf.random_normal_initializer(1., 0.02))
        gamma = tf.reshape(self.gamma, [1, 1, -1])
        self.beta = tf.get_variable("beta", [shape[-1]],
                                initializer=tf.constant_initializer(0.))
        beta = tf.reshape(self.beta, [1, 1, -1])
        assert self.epsilon is not None
        assert mean_sq is not None
        assert mean is not None
        std = tf.sqrt(self.epsilon + mean_sq - tf.square(mean))
        out = x - mean
        out = out / std
        out = out * gamma
        out = out + beta
        return out

```

## generator.py

```python
from __future__ import print_function
import tensorflow as tf
from tensorflow.contrib.layers import batch_norm, fully_connected, flatten
from tensorflow.contrib.layers import xavier_initializer
from ops import *
import numpy as np


class Generator(object):
    def __init__(self, segan):
        self.segan = segan

    def __call__(self, noisy_w, is_ref, spk=None):
        """ Build the graph propagating (noisy_w) --> x
        On first pass will make variables.
        """
        segan = self.segan

        def make_z(shape, mean=0., std=1., name='z'):
            if is_ref:
                with tf.variable_scope(name) as scope:
                    z_init = tf.random_normal_initializer(
                        mean=mean, stddev=std)
                    z = tf.get_variable(
                        "z", shape, initializer=z_init, trainable=False)
                    if z.device != "/device:GPU:0":
                        # this has to be created into gpu0
                        print('z.device is {}'.format(z.device))
                        assert False
            else:
                z = tf.random_normal(
                    shape, mean=mean, stddev=std, name=name, dtype=tf.float32)
            return z

        if hasattr(segan, 'generator_built'):
            tf.get_variable_scope().reuse_variables()
            make_vars = False
        else:
            make_vars = True

        print('*** Building Generator ***')
        in_dims = noisy_w.get_shape().as_list()
        h_i = noisy_w
        if len(in_dims) == 2:
            h_i = tf.expand_dims(noisy_w, -1)
        elif len(in_dims) < 2 or len(in_dims) > 3:
            raise ValueError('Generator input must be 2-D or 3-D')
        kwidth = 3
        z = make_z([
            segan.batch_size,
            h_i.get_shape().as_list()[1], segan.g_enc_depths[-1]
        ])
        h_i = tf.concat(2, [h_i, z])
        skip_out = True
        skips = []
        for block_idx, dilation in enumerate(segan.g_dilated_blocks):
            name = 'g_residual_block_{}'.format(block_idx)
            if block_idx >= len(segan.g_dilated_blocks) - 1:
                skip_out = False
            if skip_out:
                res_i, skip_i = residual_block(
                    h_i,
                    dilation,
                    kwidth,
                    num_kernels=32,
                    bias_init=None,
                    stddev=0.02,
                    do_skip=True,
                    name=name)
            else:
                res_i = residual_block(
                    h_i,
                    dilation,
                    kwidth,
                    num_kernels=32,
                    bias_init=None,
                    stddev=0.02,
                    do_skip=False,
                    name=name)
            # feed the residual output to the next block
            h_i = res_i
            if segan.keep_prob < 1:
                print('Adding dropout w/ keep prob {} '
                      'to G'.format(segan.keep_prob))
                h_i = tf.nn.dropout(h_i, segan.keep_prob_var)
            if skip_out:
                # accumulate the skip connections
                skips.append(skip_i)
            else:
                # for last block, the residual output is appended
                skips.append(res_i)
        print('Amount of skip connections: ', len(skips))
        # TODO: last pooling for actual wave
        with tf.variable_scope('g_wave_pooling'):
            skip_T = tf.stack(skips, axis=0)
            skips_sum = tf.reduce_sum(skip_T, axis=0)
            skips_sum = leakyrelu(skips_sum)
            wave_a = conv1d(
                skips_sum,
                kwidth=1,
                num_kernels=1,
                init=tf.truncated_normal_initializer(stddev=0.02))
            wave = tf.tanh(wave_a)
            segan.gen_wave_summ = histogram_summary('gen_wave', wave)
        print('Last residual wave shape: ', res_i.get_shape())
        print('*************************')
        segan.generator_built = True
        return wave, z


class AEGenerator(object):
    def __init__(self, segan):
        self.segan = segan

    def __call__(self, noisy_w, is_ref, spk=None, z_on=True, do_prelu=False):
        # TODO: remove c_vec
        """ Build the graph propagating (noisy_w) --> x
        On first pass will make variables.
        """
        segan = self.segan

        def make_z(shape, mean=0., std=1., name='z'):
            if is_ref:
                with tf.variable_scope(name) as scope:
                    z_init = tf.random_normal_initializer(
                        mean=mean, stddev=std)
                    z = tf.get_variable(
                        "z", shape, initializer=z_init, trainable=False)
                    if z.device != "/device:GPU:0":
                        # this has to be created into gpu0
                        print('z.device is {}'.format(z.device))
                        assert False
            else:
                z = tf.random_normal(
                    shape, mean=mean, stddev=std, name=name, dtype=tf.float32)
            return z

        if hasattr(segan, 'generator_built'):
            tf.get_variable_scope().reuse_variables()
            make_vars = False
        else:
            make_vars = True
        if is_ref:
            print('*** Building Generator ***')
        in_dims = noisy_w.get_shape().as_list()
        h_i = noisy_w
        if len(in_dims) == 2:
            h_i = tf.expand_dims(noisy_w, -1)
        elif len(in_dims) < 2 or len(in_dims) > 3:
            raise ValueError('Generator input must be 2-D or 3-D')
        kwidth = 31
        enc_layers = 7
        skips = []
        if is_ref and do_prelu:
            #keep track of prelu activations
            alphas = []
        with tf.variable_scope('g_ae'):
            #AE to be built is shaped:
            # enc ~ [16384x1, 8192x16, 4096x32, 2048x32, 1024x64, 512x64, 256x128, 128x128, 64x256, 32x256, 16x512, 8x1024]
            # dec ~ [8x2048, 16x1024, 32x512, 64x512, 8x256, 256x256, 512x128, 1024x128, 2048x64, 4096x64, 8192x32, 16384x1]
            #FIRST ENCODER
            for layer_idx, layer_depth in enumerate(segan.g_enc_depths):
                bias_init = None
                if segan.bias_downconv:
                    if is_ref:
                        print('Biasing downconv in G')
                    bias_init = tf.constant_initializer(0.)
                h_i_dwn = downconv(
                    h_i,
                    layer_depth,
                    kwidth=kwidth,
                    init=tf.truncated_normal_initializer(stddev=0.02),
                    bias_init=bias_init,
                    name='enc_{}'.format(layer_idx))
                if is_ref:
                    print('Downconv {} -> {}'.format(h_i.get_shape(),
                                                     h_i_dwn.get_shape()))
                h_i = h_i_dwn
                if layer_idx < len(segan.g_enc_depths) - 1:
                    if is_ref:
                        print('Adding skip connection downconv '
                              '{}'.format(layer_idx))
                    # store skip connection
                    # last one is not stored cause it's the code
                    skips.append(h_i)
                if do_prelu:
                    if is_ref:
                        print('-- Enc: prelu activation --')
                    h_i = prelu(
                        h_i, ref=is_ref, name='enc_prelu_{}'.format(layer_idx))
                    if is_ref:
                        # split h_i into its components
                        alpha_i = h_i[1]
                        h_i = h_i[0]
                        alphas.append(alpha_i)
                else:
                    if is_ref:
                        print('-- Enc: leakyrelu activation --')
                    h_i = leakyrelu(h_i)

            if z_on:
                # random code is fused with intermediate representation
                z = make_z([
                    segan.batch_size,
                    h_i.get_shape().as_list()[1], segan.g_enc_depths[-1]
                ])
                h_i = tf.concat([z, h_i], 2)

            #SECOND DECODER (reverse order)
            g_dec_depths = segan.g_enc_depths[:-1][::-1] + [1]
            if is_ref:
                print('g_dec_depths: ', g_dec_depths)
            for layer_idx, layer_depth in enumerate(g_dec_depths):
                h_i_dim = h_i.get_shape().as_list()
                out_shape = [h_i_dim[0], h_i_dim[1] * 2, layer_depth]
                bias_init = None
                # deconv
                if segan.deconv_type == 'deconv':
                    if is_ref:
                        print('-- Transposed deconvolution type --')
                        if segan.bias_deconv:
                            print('Biasing deconv in G')
                    if segan.bias_deconv:
                        bias_init = tf.constant_initializer(0.)
                    h_i_dcv = deconv(
                        h_i,
                        out_shape,
                        kwidth=kwidth,
                        dilation=2,
                        init=tf.truncated_normal_initializer(stddev=0.02),
                        bias_init=bias_init,
                        name='dec_{}'.format(layer_idx))
                elif segan.deconv_type == 'nn_deconv':
                    if is_ref:
                        print('-- NN interpolated deconvolution type --')
                        if segan.bias_deconv:
                            print('Biasing deconv in G')
                    if segan.bias_deconv:
                        bias_init = 0.
                    h_i_dcv = nn_deconv(
                        h_i,
                        kwidth=kwidth,
                        dilation=2,
                        init=tf.truncated_normal_initializer(stddev=0.02),
                        bias_init=bias_init,
                        name='dec_{}'.format(layer_idx))
                else:
                    raise ValueError('Unknown deconv type {}'.format(
                        segan.deconv_type))
                if is_ref:
                    print('Deconv {} -> {}'.format(h_i.get_shape(),
                                                   h_i_dcv.get_shape()))
                h_i = h_i_dcv
                if layer_idx < len(g_dec_depths) - 1:
                    if do_prelu:
                        if is_ref:
                            print('-- Dec: prelu activation --')
                        h_i = prelu(
                            h_i,
                            ref=is_ref,
                            name='dec_prelu_{}'.format(layer_idx))
                        if is_ref:
                            # split h_i into its components
                            alpha_i = h_i[1]
                            h_i = h_i[0]
                            alphas.append(alpha_i)
                    else:
                        if is_ref:
                            print('-- Dec: leakyrelu activation --')
                        h_i = leakyrelu(h_i)
                    # fuse skip connection
                    skip_ = skips[-(layer_idx + 1)]
                    if is_ref:
                        print('Fusing skip connection of '
                              'shape {}'.format(skip_.get_shape()))
                    h_i = tf.concat([h_i, skip_], 2)

                else:
                    if is_ref:
                        print('-- Dec: tanh activation --')
                    h_i = tf.tanh(h_i)

            wave = h_i
            if is_ref and do_prelu:
                print('Amount of alpha vectors: ', len(alphas))
            segan.gen_wave_summ = histogram_summary('gen_wave', wave)
            if is_ref:
                print('Amount of skip connections: ', len(skips))
                print('Last wave shape: ', wave.get_shape())
                print('*************************')
            segan.generator_built = True
            # ret feats contains the features refs to be returned
            ret_feats = [wave]
            if z_on:
                ret_feats.append(z)
            if is_ref and do_prelu:
                ret_feats += alphas
            return ret_feats

```