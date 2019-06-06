from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np

from ops import *

layers = tf.contrib.layers
tfgan = tf.contrib.gan

def generator_fn(segan, noisy_w):

    def make_z(shape, mean=0., std=1., name='z'):
        z = tf.random_normal(
            shape, mean=mean, stddev=std, name=name, dtype=tf.float32)
        return z

    in_dims = noisy_w.get_shape().as_list()
    h_i = noisy_w
    if len(in_dims) == 2:
        h_i = tf.expand_dims(noisy_w, -1)
    elif len(in_dims) < 2 or len(in_dims) > 3:
        raise ValueError('Generator input must be 2-D or 3-D')
    kwidth = 31
    skips = []
    with tf.variable_scope('g_ae'):
        #AE to be built is shaped:
        # enc ~ [16384x1, 8192x16, 4096x32, 2048x32, 1024x64, 512x64, 256x128, 128x128, 64x256, 32x256, 16x512, 8x1024]
        # dec ~ [8x2048, 16x1024, 32x512, 64x512, 128x256, 256x256, 512x128, 1024x128, 2048x64, 4096x64, 8192x32, 16384x1]
        #FIRST ENCODER
        # g_enc_depths = [16, 32, 32, 64, 64, 128, 128, 256, 256, 512, 1024]
        for layer_idx, layer_depth in enumerate(segan.g_enc_depths):
            bias_init = None
            if segan.bias_downconv:
                bias_init = tf.constant_initializer(0.)
            h_i_dwn = downconv(
                h_i,
                layer_depth,
                kwidth=kwidth,
                init=tf.truncated_normal_initializer(stddev=0.02),
                bias_init=bias_init,
                name='enc_{}'.format(layer_idx))
            h_i = h_i_dwn
            if layer_idx < len(segan.g_enc_depths) - 1:
                # store skip connection
                # last one is not stored cause it's the code
                skips.append(h_i)
            h_i = prelu(
                h_i, ref=False, name='enc_prelu_{}'.format(layer_idx))

        # random code is fused with intermediate representation
        z = make_z([
            segan.batch_size,
            h_i.get_shape().as_list()[1], segan.g_enc_depths[-1]
        ])
        print('z shape {}'.format(z.get_shape()))
        h_i = tf.concat([z, h_i], 2)
        print('h shape {}'.format(h_i.get_shape()))

        #SECOND DECODER (reverse order)
        g_dec_depths = segan.g_enc_depths[:-1][::-1] + [1]
        for layer_idx, layer_depth in enumerate(g_dec_depths):
            h_i_dim = h_i.get_shape().as_list()
            out_shape = [h_i_dim[0], h_i_dim[1] * 2, layer_depth]
            bias_init = None
            # deconv
            if segan.deconv_type == 'deconv':
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
            h_i = h_i_dcv
            if layer_idx < len(g_dec_depths) - 1:
                h_i = prelu(
                    h_i,
                    ref=False,
                    name='dec_prelu_{}'.format(layer_idx))
                # fuse skip connection
                skip_ = skips[-(layer_idx + 1)]
                h_i = tf.concat([h_i, skip_], 2)
            else:
                h_i = tf.tanh(h_i)

        wave = h_i
        segan.gen_wave_summ = histogram_summary('gen_wave', wave)
        # ret feats contains the features refs to be returned
        ret_feats = [wave]
        ret_feats.append(z)
        return wave

def discriminator_fn(segan, wave_in):
        """
        wave_in: waveform input
        """
        # take the waveform as input "activation"
        in_dims = wave_in.get_shape().as_list()
        hi = wave_in
        if len(in_dims) == 2:
            hi = tf.expand_dims(wave_in, -1)
        elif len(in_dims) < 2 or len(in_dims) > 3:
            raise ValueError('Discriminator input must be 2-D or 3-D')

        # set up the disc_block function
        with tf.variable_scope('d_model') as scope:
            scope.reuse_variables()
            def disc_block(block_idx, input_, kwidth, nfmaps, bnorm, activation,
                           pooling=2):
                with tf.variable_scope('d_block_{}'.format(block_idx)):
                    bias_init = None
                    if segan.bias_D_conv:
                        bias_init = tf.constant_initializer(0.)
                    downconv_init = tf.truncated_normal_initializer(stddev=0.02)
                    hi_a = downconv(input_, nfmaps, kwidth=kwidth, pool=pooling,
                                    init=downconv_init, bias_init=bias_init)
                    if bnorm:
                        hi_a = segan.vbn(hi_a, 'd_vbn_{}'.format(block_idx))
                    if activation == 'leakyrelu':
                        hi = leakyrelu(hi_a)
                    elif activation == 'relu':
                        hi = tf.nn.relu(hi_a)
                    else:
                        raise ValueError('Unrecognized activation {} '
                                         'in D'.format(activation))
                    return hi
            # apply input noisy layer to real and fake samples
            # disc_noise_std = 0 意味着gaussian_noise_layer无效
            hi = gaussian_noise_layer(hi, segan.disc_noise_std)
            # d_num_fmaps = [16, 32, 32, 64, 64, 128, 128, 256, 256, 512, 1024]
            for block_idx, fmaps in enumerate(segan.d_num_fmaps):
                hi = disc_block(block_idx, hi, 31,
                                fmaps,
                                True, 'leakyrelu')
            # hi_f = flatten(hi)
            #hi_f = tf.nn.dropout(hi_f, segan.keep_prob_var)
            d_logit_out = conv1d(hi, kwidth=1, num_kernels=1,
                                 init=tf.truncated_normal_initializer(stddev=0.02),
                                 name='logits_conv')
            d_logit_out = tf.squeeze(d_logit_out)
            d_logit_out = fully_connected(d_logit_out, 1, activation_fn=None)
            return d_logit_out
