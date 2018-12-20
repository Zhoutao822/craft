#%% [markdown]
# ##### Copyright 2018 The AdaNet Authors.

#%%
#@title Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#%% [markdown]
# # The AdaNet objective
# 
# One of key contributions from *AdaNet: Adaptive Structural Learning of Neural
# Networks* [[Cortes et al., ICML 2017](https://arxiv.org/abs/1607.01097)] is
# defining an algorithm that aims to directly minimize the DeepBoost
# generalization bound from *Deep Boosting*
# [[Cortes et al., ICML 2014](http://proceedings.mlr.press/v32/cortesb14.pdf)]
# when applied to neural networks. This algorithm, called **AdaNet**, adaptively
# grows a neural network as an ensemble of subnetworks that minimizes the AdaNet
# objective (a.k.a. AdaNet loss):
# 
# $$F(w) = \frac{1}{m} \sum_{i=1}^{m} \Phi \left(\sum_{j=1}^{N}w_jh_j(x_i), y_i \right) + \sum_{j=1}^{N} \left(\lambda r(h_j) + \beta \right) |w_j| $$
# 
# where $w$ is the set of mixture weights, one per subnetwork $h$,
# $\Phi$ is a surrogate loss function such as logistic loss or MSE, $r$ is a
# function for measuring a subnetwork's complexity, and $\lambda$ and $\beta$
# are hyperparameters.
# 
# ## Mixture weights
# 
# So what are mixture weights? When forming an ensemble $f$ of subnetworks $h$,
# we need to somehow combine the their predictions. This is done by multiplying
# the outputs of subnetwork $h_i$ with mixture weight $w_i$, and summing the
# results:
# 
# $$f(x) = \sum_{j=1}^{N}w_jh_j(x)$$
# 
# In practice, most commonly used set of mixture weight is **uniform average
# weighting**:
# 
# $$f(x) = \frac{1}{N}\sum_{j=1}^{N}h_j(x)$$
# 
# However, we can also solve a convex optimization problem to learn the mixture
# weights that minimize the loss function $\Phi$:
# 
# $$F(w) = \frac{1}{m} \sum_{i=1}^{m} \Phi \left(\sum_{j=1}^{N}w_jh_j(x_i), y_i \right)$$
# 
# This is the first term in the AdaNet objective. The second term applies L1
# regularization to the mixture weights:
# 
# $$\sum_{j=1}^{N} \left(\lambda r(h_j) + \beta \right) |w_j|$$
# 
# When $\lambda > 0$ this penalty serves to prevent the optimization from
# assigning too much weight to more complex subnetworks according to the
# complexity measure function $r$.
# 
# ## How AdaNet uses the objective
# 
# This objective function serves two purposes:
# 
# 1.  To **learn to scale/transform the outputs of each subnetwork $h$** as part
#     of the ensemble.
# 2.  To **select the best candidate subnetwork $h$** at each AdaNet iteration
#     to include in the ensemble.
# 
# Effectively, when learning mixture weights $w$, AdaNet solves a convex
# combination of the outputs of the frozen subnetworks $h$. For $\lambda >0$,
# AdaNet penalizes more complex subnetworks with greater L1 regularization on
# their mixture weight, and will be less likely to select more complex subnetworks
# to add to the ensemble at each iteration.
# 
# In this tutorial, in you will observe the benefits of using AdaNet to learn the
# ensemble's mixture weights and to perform candidate selection.
# 
# 

#%%
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools

import adanet
import tensorflow as tf

# The random seed to use.
RANDOM_SEED = 42

#%% [markdown]
# ## Boston Housing dataset
# 
# In this example, we will solve a regression task known as the [Boston Housing dataset](https://www.cs.toronto.edu/~delve/data/boston/bostonDetail.html) to predict the price of suburban houses in Boston, MA in the 1970s. There are 13 numerical features, the labels are in thousands of dollars, and there are only 506 examples.
# 
#%% [markdown]
# ## Download the data
# Conveniently, the data is available via Keras:

#%%
(x_train, y_train), (x_test, y_test) = (
    tf.keras.datasets.boston_housing.load_data())

#%% [markdown]
# ## Supply the data in TensorFlow
# 
# Our first task is to supply the data in TensorFlow. Using the
# tf.estimator.Estimator covention, we will define a function that returns an
# input_fn which returns feature and label Tensors.
# 
# We will also use the tf.data.Dataset API to feed the data into our models.
# 
# Also, as a preprocessing step, we will apply `tf.log1p` to log-scale the
# features and labels for improved numerical stability during training. To recover
# the model's predictions in the correct scale, you can apply `tf.expm1` to the
# prediction.

#%%
FEATURES_KEY = "x"


def input_fn(partition, training, batch_size):
  """Generate an input function for the Estimator."""

  def _input_fn():

    if partition == "train":
      dataset = tf.data.Dataset.from_tensor_slices(({
          FEATURES_KEY: tf.log1p(x_train)
      }, tf.log1p(y_train)))
    else:
      dataset = tf.data.Dataset.from_tensor_slices(({
          FEATURES_KEY: tf.log1p(x_test)
      }, tf.log1p(y_test)))

    # We call repeat after shuffling, rather than before, to prevent separate
    # epochs from blending together.
    if training:
      dataset = dataset.shuffle(10 * batch_size, seed=RANDOM_SEED).repeat()

    dataset = dataset.batch(batch_size)
    iterator = dataset.make_one_shot_iterator()
    features, labels = iterator.get_next()
    return features, labels

  return _input_fn

#%% [markdown]
# ## Define the subnetwork generator
# 
# Let's define a subnetwork generator similar to the one in
# [[Cortes et al., ICML 2017](https://arxiv.org/abs/1607.01097)] and in
# `simple_dnn.py` which creates two candidate fully-connected neural networks at
# each iteration with the same width, but one an additional hidden layer. To make
# our generator *adaptive*, each subnetwork will have at least the same number
# of hidden layers as the most recently added subnetwork to the
# `previous_ensemble`.
# 
# We define the complexity measure function $r$ to be $r(h) = \sqrt{d(h)}$, where
# $d$ is the number of hidden layers in the neural network $h$, to approximate the
# Rademacher bounds from
# [[Golowich et. al, 2017](https://arxiv.org/abs/1712.06541)]. So subnetworks
# with more hidden layers, and therefore more capacity, will have more heavily
# regularized mixture weights.

#%%
_NUM_LAYERS_KEY = "num_layers"


class _SimpleDNNBuilder(adanet.subnetwork.Builder):
  """Builds a DNN subnetwork for AdaNet."""

  def __init__(self, optimizer, layer_size, num_layers, learn_mixture_weights,
               seed):
    """Initializes a `_DNNBuilder`.

    Args:
      optimizer: An `Optimizer` instance for training both the subnetwork and
        the mixture weights.
      layer_size: The number of nodes to output at each hidden layer.
      num_layers: The number of hidden layers.
      learn_mixture_weights: Whether to solve a learning problem to find the
        best mixture weights, or use their default value according to the
        mixture weight type. When `False`, the subnetworks will return a no_op
        for the mixture weight train op.
      seed: A random seed.

    Returns:
      An instance of `_SimpleDNNBuilder`.
    """

    self._optimizer = optimizer
    self._layer_size = layer_size
    self._num_layers = num_layers
    self._learn_mixture_weights = learn_mixture_weights
    self._seed = seed

  def build_subnetwork(self,
                       features,
                       logits_dimension,
                       training,
                       iteration_step,
                       summary,
                       previous_ensemble=None):
    """See `adanet.subnetwork.Builder`."""

    input_layer = tf.to_float(features[FEATURES_KEY])
    kernel_initializer = tf.glorot_uniform_initializer(seed=self._seed)
    last_layer = input_layer
    for _ in range(self._num_layers):
      last_layer = tf.layers.dense(
          last_layer,
          units=self._layer_size,
          activation=tf.nn.relu,
          kernel_initializer=kernel_initializer)
    logits = tf.layers.dense(
        last_layer,
        units=logits_dimension,
        kernel_initializer=kernel_initializer)

    persisted_tensors = {_NUM_LAYERS_KEY: tf.constant(self._num_layers)}
    return adanet.Subnetwork(
        last_layer=last_layer,
        logits=logits,
        complexity=self._measure_complexity(),
        persisted_tensors=persisted_tensors)

  def _measure_complexity(self):
    """Approximates Rademacher complexity as the square-root of the depth."""
    return tf.sqrt(tf.to_float(self._num_layers))

  def build_subnetwork_train_op(self, subnetwork, loss, var_list, labels,
                                iteration_step, summary, previous_ensemble):
    """See `adanet.subnetwork.Builder`."""
    return self._optimizer.minimize(loss=loss, var_list=var_list)

  def build_mixture_weights_train_op(self, loss, var_list, logits, labels,
                                     iteration_step, summary):
    """See `adanet.subnetwork.Builder`."""

    if not self._learn_mixture_weights:
      return tf.no_op()
    return self._optimizer.minimize(loss=loss, var_list=var_list)

  @property
  def name(self):
    """See `adanet.subnetwork.Builder`."""

    if self._num_layers == 0:
      # A DNN with no hidden layers is a linear model.
      return "linear"
    return "{}_layer_dnn".format(self._num_layers)


class SimpleDNNGenerator(adanet.subnetwork.Generator):
  """Generates a two DNN subnetworks at each iteration.

  The first DNN has an identical shape to the most recently added subnetwork
  in `previous_ensemble`. The second has the same shape plus one more dense
  layer on top. This is similar to the adaptive network presented in Figure 2 of
  [Cortes et al. ICML 2017](https://arxiv.org/abs/1607.01097), without the
  connections to hidden layers of networks from previous iterations.
  """

  def __init__(self,
               optimizer,
               layer_size=32,
               learn_mixture_weights=False,
               seed=None):
    """Initializes a DNN `Generator`.

    Args:
      optimizer: An `Optimizer` instance for training both the subnetwork and
        the mixture weights.
      layer_size: Number of nodes in each hidden layer of the subnetwork
        candidates. Note that this parameter is ignored in a DNN with no hidden
        layers.
      learn_mixture_weights: Whether to solve a learning problem to find the
        best mixture weights, or use their default value according to the
        mixture weight type. When `False`, the subnetworks will return a no_op
        for the mixture weight train op.
      seed: A random seed.

    Returns:
      An instance of `Generator`.
    """

    self._seed = seed
    self._dnn_builder_fn = functools.partial(
        _SimpleDNNBuilder,
        optimizer=optimizer,
        layer_size=layer_size,
        learn_mixture_weights=learn_mixture_weights)

  def generate_candidates(self, previous_ensemble, iteration_number,
                          previous_ensemble_reports, all_reports):
    """See `adanet.subnetwork.Generator`."""

    num_layers = 0
    seed = self._seed
    if previous_ensemble:
      num_layers = tf.contrib.util.constant_value(
          previous_ensemble.weighted_subnetworks[
              -1].subnetwork.persisted_tensors[_NUM_LAYERS_KEY])
    if seed is not None:
      seed += iteration_number
    return [
        self._dnn_builder_fn(num_layers=num_layers, seed=seed),
        self._dnn_builder_fn(num_layers=num_layers + 1, seed=seed),
    ]

#%% [markdown]
# ## Train and evaluate
# 
# Next we create an `adanet.Estimator` using the `SimpleDNNGenerator` we just defined.
# 
# In this section we will show the effects of two hyperparamters: **learning mixture weights** and **complexity regularization**.
# 
# On the righthand side you will be able to play with the hyperparameters of this model. Until you reach the end of this section, we ask that you not change them. 
# 
# At first we will not learn the mixture weights, using their default initial value. Here they will be scalars initialized to $1/N$ where $N$ is the number of subnetworks in the ensemble, effectively creating a **uniform average ensemble**.

#%%
#@title AdaNet parameters
LEARNING_RATE = 0.001  #@param {type:"number"}
TRAIN_STEPS = 100000  #@param {type:"integer"}
BATCH_SIZE = 32  #@param {type:"integer"}

LEARN_MIXTURE_WEIGHTS = False  #@param {type:"boolean"}
ADANET_LAMBDA = 0  #@param {type:"number"}
BOOSTING_ITERATIONS = 5  #@param {type:"integer"}


def train_and_evaluate(learn_mixture_weights=LEARN_MIXTURE_WEIGHTS,
                       adanet_lambda=ADANET_LAMBDA):
  """Trains an `adanet.Estimator` to predict housing prices."""

  estimator = adanet.Estimator(
      # Since we are predicting housing prices, we'll use a regression
      # head that optimizes for MSE.
      head=tf.contrib.estimator.regression_head(
          loss_reduction=tf.losses.Reduction.SUM_OVER_BATCH_SIZE),

      # Define the generator, which defines our search space of subnetworks
      # to train as candidates to add to the final AdaNet model.
      subnetwork_generator=SimpleDNNGenerator(
          optimizer=tf.train.RMSPropOptimizer(learning_rate=LEARNING_RATE),
          learn_mixture_weights=learn_mixture_weights,
          seed=RANDOM_SEED),

      # Lambda is a the strength of complexity regularization. A larger
      # value will penalize more complex subnetworks.
      adanet_lambda=adanet_lambda,

      # The number of train steps per iteration.
      max_iteration_steps=TRAIN_STEPS // BOOSTING_ITERATIONS,

      # The evaluator will evaluate the model on the full training set to
      # compute the overall AdaNet loss (train loss + complexity
      # regularization) to select the best candidate to include in the
      # final AdaNet model.
      evaluator=adanet.Evaluator(
          input_fn=input_fn("train", training=False, batch_size=BATCH_SIZE)),

      # The report materializer will evaluate the subnetworks' metrics
      # using the full training set to generate the reports that the generator
      # can use in the next iteration to modify its search space.
      report_materializer=adanet.ReportMaterializer(
          input_fn=input_fn("train", training=False, batch_size=BATCH_SIZE)),

      # Configuration for Estimators.
      config=tf.estimator.RunConfig(
          save_checkpoints_steps=50000,
          save_summary_steps=50000,
          tf_random_seed=RANDOM_SEED))

  # Train and evaluate using using the tf.estimator tooling.
  train_spec = tf.estimator.TrainSpec(
      input_fn=input_fn("train", training=True, batch_size=BATCH_SIZE),
      max_steps=TRAIN_STEPS)
  eval_spec = tf.estimator.EvalSpec(
      input_fn=input_fn("test", training=False, batch_size=BATCH_SIZE),
      steps=None)
  return tf.estimator.train_and_evaluate(estimator, train_spec, eval_spec)


def ensemble_architecture(result):
  """Extracts the ensemble architecture from evaluation results."""

  architecture = result["architecture/adanet/ensembles"]
  # The architecture is a serialized Summary proto for TensorBoard.
  summary_proto = tf.summary.Summary.FromString(architecture)
  return summary_proto.value[0].tensor.string_val[0]


results, _ = train_and_evaluate()
print("Loss:", results["average_loss"])
print("Architecture:", ensemble_architecture(results))

#%% [markdown]
# These hyperparameters preduce a model that achieves **0.0348** MSE on the test
# set. Notice that the ensemble is composed of 5 subnetworks, each one a hidden
# layer deeper than the previous. The most complex subnetwork is made of 5 hidden
# layers.
# 
# Since `SimpleDNNGenerator` produces subnetworks of varying complexity, and our
# model gives each one an equal weight, AdaNet selected the subnetwork that most
# lowered the ensemble's training loss at each iteration, likely the one with the
# most hidden layers, since it has the most capacity, and we aren't penalizing
# more complex subnetworks (yet).
# 
# Next, instead of assigning equal weight to each subnetwork, let's learn the
# mixture weights as a convex optimization problem using SGD:

#%%
#@test {"skip": true}
results, _ = train_and_evaluate(learn_mixture_weights=True)
print("Loss:", results["average_loss"])
print("Uniform average loss:", results["average_loss/adanet/uniform_average_ensemble"])
print("Architecture:", ensemble_architecture(results))

#%% [markdown]
# Learning the mixture weights produces a model with **0.0449** MSE, a bit worse
# than the uniform average model, which the `adanet.Estimator` always compute as a
# baseline. The mixture weights were learned without regularization, so they
# likely overfit to the training set.
# 
# Observe that AdaNet learned the same ensemble composition as the previous run.
# Without complexity regularization, AdaNet will favor more complex subnetworks,
# which may have worse generalization despite improving the empirical error.
# 
# Finally, let's apply some **complexity regularization** by using $\lambda > 0$.
# Since this will penalize more complex subnetworks, AdaNet will select the
# candidate subnetwork that most improves the objective for its marginal
# complexity:

#%%
#@test {"skip": true}
results, _ = train_and_evaluate(learn_mixture_weights=True, adanet_lambda=.015)
print("Loss:", results["average_loss"])
print("Uniform average loss:", results["average_loss/adanet/uniform_average_ensemble"])
print("Architecture:", ensemble_architecture(results))

#%% [markdown]
# Learning the mixture weights with $\lambda > 0$ produces a model with **0.0320**
# MSE. Notice that this is even better than the uniform average ensemble produced
# from the chosen subnetworks with **0.0345** MSE.
# 
# Inspecting the ensemble architecture demonstrates the effects of complexity
# regularization on candidate selection. The selected subnetworks are relatively
# less complex: unlike in previous runs, the simplest subnetwork is a linear model
# and the deepest subnetwork has only 3 hidden layers.
# 
# In general, learning to combine subnetwork ouputs with optimal hyperparameters
# should be at least as good assigning uniform average weights.
#%% [markdown]
# ## Conclusion
# 
# In this tutorial, you were able to explore training an AdaNet model's mixture
# weights with $\lambda \ge 0$. You were also able to compare against building an
# ensemble formed by always choosing the best candidate subnetwork at each
# iteration based on it's ability to improve the ensemble's loss on the training
# set, and averaging their results.
# 
# Uniform average ensembles work unreasonably well in practice, yet learning the
# mixture weights with the correct values of $\lambda$ and $\beta$ should always
# produce a better model when candidates have varying complexity. However, this
# does require some additional hyperparameter tuning, so practically you can train
# an AdaNet with the default mixture weights and $\lambda=0$ first, and once you
# have confirmed that the subnetworks are training correctly, you can tune the
# mixture weight hyperparameters.
# 
# While this example explored a regression task, these observations apply to using
# AdaNet on other tasks like binary-classification and multi-class classification.

