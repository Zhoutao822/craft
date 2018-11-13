#%%
from __future__ import print_function, absolute_import, division
import tensorflow as tf
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

tf.enable_eager_execution()
tfe = tf.contrib.eager
print('Tensorflow version: ', tf.VERSION)
print('Eager mode: ', tf.executing_eagerly())

learning_rate = 0.01
batch_size = 32
num_steps = 1000
display_step = 100

(data, target) = load_iris(return_X_y=True)

x_train, x_test, y_train, y_test = train_test_split(data, target, test_size=0.2, shuffle=True)

#%%    
dataset = tf.data.Dataset.from_tensor_slices((tf.cast(x_train, tf.float32), y_train)).shuffle(1000).batch(batch_size)
dataset_iter = tfe.Iterator(dataset)

W = tfe.Variable(tf.zeros([4, 3]), name='weights')
b = tfe.Variable(tf.zeros([3]), name='bias')

def regression(x):
    return tf.matmul(x, W) + b

def loss(inference_fn, x, y):
    return tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(
        logits=inference_fn(x), labels=y))

def accuracy(inference_fn, x, y):
    pro = tf.nn.softmax(inference_fn(x))
    pre = tf.equal(tf.argmax(pro, 1), y)
    return tf.reduce_mean(tf.cast(pre, tf.float32))

optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)

grad = tfe.implicit_gradients(loss)

avg_loss = 0.
avg_acc = 0.

for i in range(num_steps):
    try:
        d = dataset_iter.next()
    except StopIteration:
        dataset_iter = tfe.Iterator(dataset)
        d = dataset_iter.next()

    x_batch = d[0]
    y_batch = tf.cast(d[1], tf.int64)

    batch_loss = loss(regression, x_batch, y_batch)
    avg_loss += batch_loss
    batch_acc = accuracy(regression, x_batch, y_batch)
    avg_acc += batch_acc

    if i == 0:
        print('Initial loss = {:.5f}'.format(avg_loss))
    
    optimizer.apply_gradients(grad(regression, x_batch, y_batch))

    if (i + 1 ) % display_step == 0 or i == 0:
        if i > 0:
            avg_loss /= display_step
            avg_acc /= display_step
        print('Step:{:04d}'.format(i + 1), 'loss = {:.5f}'.format(avg_loss),
        'accuracy = {:.4f}'.format(avg_acc))
        avg_acc = 0.
        avg_loss = 0.
#%%
test_acc = accuracy(regression, tf.cast(x_test, tf.float32), y_test)
print('Test accuracy: {:.4f}'.format(test_acc))

