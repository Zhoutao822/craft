#%%
import tensorflow as tf
import cifar10
sess = tf.Session()

dataset = cifar10.Cifar10DataSet('./cifar10')
data = dataset.make_batch(16)
img, label = sess.run(data)

print(img.shape, label)

