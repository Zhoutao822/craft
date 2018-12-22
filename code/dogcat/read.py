#%%
import h5py

import numpy as np

x_train = []
y_train = []
x_test = []
x_index = []
for i in range(1):
    with h5py.File('gap_MobileNetV2.h5', 'r') as h:
        x_train.append(np.array(h['train']))
        x_test.append(np.array(h['test']))
        y_train = np.array(h['label'])
        x_index = np.array(h['index'])

x_train = np.concatenate(x_train, axis=1)
x_test = np.concatenate(x_test, axis=1)
y_train = np.array(y_train)
print(x_train.shape, x_test.shape, y_train.shape)

print(x_train[0], y_train[0])
print(x_index[:10], x_test[:10])
#%%
import os
path = 'img_test/test/'
files = os.listdir(path)
print(files)
#%%
for name in files:
    old = path + name
    num = name.split('.')[0]
    new = path + '{}'.format(int('0b' + num, 2)) + '.jpg'
    os.rename(old, new)
    print(old, '===>', new)
#%%
print(os.listdir(path))

#%%
import os
import shutil
path = 'train'
for i in range(0, 12500):
    name = 'dog.{}.jpg'.format(i)
    src = os.path.join(path, name)
    dst = os.path.join(os.path.join('img_train', 'dog'), name)
    shutil.copyfile(src, dst)

#%%
for i in range(0, 12500):
    name = 'cat.{}.jpg'.format(i)
    src = os.path.join(path, name)
    dst = os.path.join(os.path.join('img_train', 'cat'), name)
    shutil.copyfile(src, dst)