from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np

import os

import networks
import data_provider

from scipy.io import wavfile
from data_loader import pre_emph

tfgan = tf.contrib.gan

flags = tf.app.flags
flags.DEFINE_integer("seed", 111, "Random seed (Def: 111).")
flags.DEFINE_integer("epoch", 86, "Epochs to train (Def: 150).")
flags.DEFINE_integer("batch_size", 100, "Batch size (Def: 150).")
flags.DEFINE_integer("save_freq", 50, "Batch save freq (Def: 50).")
flags.DEFINE_integer("canvas_size", 2**14, "Canvas size (Def: 2^14).")
flags.DEFINE_integer("denoise_epoch", 5, "Epoch where noise in disc is "
                     "removed (Def: 5).")
flags.DEFINE_integer("l1_remove_epoch", 150, "Epoch where L1 in G is "
                     "removed (Def: 150).")
flags.DEFINE_boolean("bias_deconv", True,
                     "Flag to specify if we bias deconvs (Def: False)")
flags.DEFINE_boolean("bias_downconv", True,
                     "flag to specify if we bias downconvs (def: false)")
flags.DEFINE_boolean("bias_D_conv", True,
                     "flag to specify if we bias D_convs (def: false)")
# TODO: noise decay is under check
flags.DEFINE_float("denoise_lbound", 0.01,
                   "Min noise std to be still alive (Def: 0.001)")
flags.DEFINE_float("noise_decay", 0.7, "Decay rate of noise std (Def: 0.7)")
flags.DEFINE_float("d_label_smooth", 0.25, "Smooth factor in D (Def: 0.25)")
flags.DEFINE_float("init_noise_std", 0., "Init noise std (Def: 0.5)")
flags.DEFINE_float("init_l1_weight", 100., "Init L1 lambda (Def: 100)")
flags.DEFINE_integer("z_dim", 256, "Dimension of input noise to G (Def: 256).")
flags.DEFINE_integer("z_depth", 256, "Depth of input noise to G (Def: 256).")
flags.DEFINE_string("save_path", "segan_allbiased_preemph", "Path to save out model "
                    "files. (Def: dwavegan_model"
                    ").")
flags.DEFINE_string("g_nl", "prelu",
                    "Type of nonlinearity in G: leaky or prelu. (Def: leaky).")
flags.DEFINE_string("model", "gan",
                    "Type of model to train: gan or ae. (Def: gan).")
flags.DEFINE_string("deconv_type", "deconv",
                    "Type of deconv method: deconv or "
                    "nn_deconv (Def: deconv).")
flags.DEFINE_string("g_type", "ae",
                    "Type of G to use: ae or dwave. (Def: ae).")
flags.DEFINE_float("g_learning_rate", 0.0002, "G learning_rate (Def: 0.0002)")
flags.DEFINE_float("d_learning_rate", 0.0002, "D learning_rate (Def: 0.0002)")
flags.DEFINE_float("beta_1", 0.5, "Adam beta 1 (Def: 0.5)")
flags.DEFINE_float("preemph", 0.95, "Pre-emph factor (Def: 0.95)")
flags.DEFINE_string("synthesis_path", "dwavegan_samples", "Path to save output"
                    " generated samples."
                    " (Def: dwavegan_sam"
                    "ples).")
flags.DEFINE_string("e2e_dataset", "data/segan.tfrecords", "TFRecords"
                    " (Def: data/"
                    "segan.tfrecords.")
flags.DEFINE_string("save_clean_path", "test_clean_results",
                    "Path to save clean utts")
flags.DEFINE_string("test_wav", None, "name of test wav (it won't train)")
flags.DEFINE_string("weights", None, "Weights file")
FLAGS = flags.FLAGS

def main(_):
    print('Parsed arguments: ', FLAGS.__flags)

    # make save path if it is required
    if not os.path.exists(FLAGS.save_path):
        os.makedirs(FLAGS.save_path)
    if not os.path.exists(FLAGS.synthesis_path):
        os.makedirs(FLAGS.synthesis_path)

    # execute the session
    with tf.Session(config=config) as sess:
        if FLAGS.model == 'gan':
            print('Creating GAN model')
            se_model = SEGAN(sess, FLAGS, udevices)
        elif FLAGS.model == 'ae':
            print('Creating AE model')
            se_model = SEAE(sess, FLAGS, udevices)
        else:
            raise ValueError('{} model type not understood!'.format(
                FLAGS.model))
        if FLAGS.test_wav is None:
            se_model.train(FLAGS, udevices)
        


if __name__ == '__main__':
  tf.logging.set_verbosity(tf.logging.INFO)
  tf.app.run()
