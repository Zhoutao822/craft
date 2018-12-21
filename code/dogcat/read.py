#%%
import h5py

import numpy as np

x_train = []
y_train = []
x_test = []
for i in range(3):
    with h5py.File('gap_InceptionV3.h5', 'r') as h:
        x_train.append(np.array(h['train']))
        x_test.append(np.array(h['test']))
        y_train = np.array(h['label'])

x_train = np.concatenate(x_train, axis=1)
x_test = np.concatenate(x_test, axis=1)
y_train = np.array(y_train)
print(x_train.shape, x_test.shape, y_train.shape)

print(x_train[0], y_train[0])

#%%
import os
path = 'log/'
files = os.listdir(path)
print(files)
#%%
for name in files:
    old = path + name
    num = name.split('.')[0]
    new = path + '{:014b}'.format(int(num)) + '.jpg'
    os.rename(old, new)
    print(old, '===>', new)
#%%
print(os.listdir(path))