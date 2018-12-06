#%%
from __future__ import absolute_import, print_function, division
import tensorflow as tf

tf.enable_eager_execution()
tfe = tf.contrib.eager

print('Tensorflow version: ', tf.VERSION, '\n', 'Eager mode: ', tf.executing_eagerly())

#%%
learning_rate = 1e-4
num_steps = 8000
batch_size = 64
display_step = 100

num_classes = 10

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

print('train size:', x_train.shape, y_train.shape)
print('test size:', x_test.shape, y_test.shape)

dataset = tf.data.Dataset.from_tensor_slices(
    (tf.reshape(tf.cast(x_train, tf.float32), shape=[-1, 28, 28, 1]), 
    tf.one_hot(y_train, depth=10, axis=-1))).shuffle(1000).batch(batch_size)
dataset_iter = tfe.Iterator(dataset)

class CNN(tfe.Network):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv2d_1 = self.track_layer(
            tf.layers.Conv2D(32, 5, padding='SAME', activation='relu'))
        self.conv2d_2 = self.track_layer(
            tf.layers.Conv2D(64, 5, padding='SAME', activation='relu'))
        self.maxpool = self.track_layer(
            tf.layers.MaxPooling2D(2, 2, padding='SAME'))
        self.flatten = self.track_layer(
            tf.layers.Flatten()) 
        self.fclayer = self.track_layer(
            tf.layers.Dense(1024, activation='relu'))
        self.dropout = self.track_layer(
            tf.layers.Dropout(0.5))
        self.out_layer = self.track_layer(
            tf.layers.Dense(num_classes))
    
    def call(self, x, training=True):
        x = self.conv2d_1(x)
        x = self.maxpool(x)
        x = self.conv2d_2(x)
        x = self.maxpool(x)
        x = self.flatten(x)
        x = self.fclayer(x)
        if training:
            x = self.dropout(x)
        return self.out_layer(x)

cnn = CNN()

def loss_fn(inference_fn, inputs, labels):
    return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(
        logits = inference_fn(inputs), labels = labels))

def accuracy_fn(inference_fn, inputs, labels, training):
    prediction = tf.nn.softmax(inference_fn(inputs, training))
    correct_pred = tf.equal(tf.argmax(prediction, 1), tf.argmax(labels, 1))
    return tf.reduce_mean(tf.cast(correct_pred, tf.float32))

optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
grad = tfe.implicit_gradients(loss_fn)

average_loss = 0.
average_acc = 0.

for step in range(num_steps):
    try:
        d = dataset_iter.next()
    except StopIteration:
        dataset_iter = tfe.Iterator(dataset)
        d = dataset_iter.next()

    x_batch = d[0]
    y_batch = tf.cast(d[1], tf.int64)

    batch_loss = loss_fn(cnn, x_batch, y_batch)
    average_loss += batch_loss

    batch_accuracy = accuracy_fn(cnn, x_batch, y_batch, True)
    average_acc += batch_accuracy

    if step == 0:
        print("Initial loss= {:.6f}".format(average_loss))

    optimizer.apply_gradients(grad(cnn, x_batch, y_batch))

    if (step + 1) % display_step == 0 or step == 0:
        if step > 0:
            average_loss /= display_step
            average_acc /= display_step
        print("Step:", '%04d' % (step + 1), " loss=",
              "{:.6f}".format(average_loss), " accuracy=",
              "{:.4f}".format(average_acc))
        average_loss = 0.
        average_acc = 0.
        test_acc = accuracy_fn(cnn, tf.reshape(tf.cast(x_test, tf.float32), shape=[-1, 28, 28, 1]), tf.one_hot(y_test, depth=10, axis=-1), False)
        print('Testset accuracy: {:.4f}'.format(test_acc))

