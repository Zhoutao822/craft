#coding=utf-8
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import  load_breast_cancer
from sklearn.model_selection import train_test_split


def init_variables(layers):
	"""
        desc:
            根据layers初始化神经网络参数
        parameters: 
            layers: 神经网络的结构，每一层的神经元个数，list
        return:
            variables: 初始化的神经网络参数，w和b，dict
    """
	L = len(layers)
	variables = {}
	for i in range(1, L):
		variables["W" + str(i)] = np.random.randn(layers[i], layers[i - 1]) * 0.01
		variables["b" + str(i)] = np.zeros((layers[i], 1))
	return variables

def relu(Z):
	return np.maximum(0, Z)

def sigmoid(Z):
	return 1 / (1 + np.exp(-Z))

def fp(X, variables):
	"""
        desc: 
            前向传播，计算预测值
        parameters:
            X: 输入数据集，形式m*n0，m为样本数，n0为特征数
            variables: 神经网络参数，w和b
        return:
            AL: 预测结果
            caches: 计算过程中缓存的每一层神经元的输入输出以及参数
    """
	A = X
	L = len(variables) // 2
	caches = [(None, None, None, X)]
	for l in range(1, L):
		A_pre = A
		W = variables['W' + str(l)]
		b = variables['b' + str(l)]
		z = np.dot(W, A_pre) + b
		A = relu(z)
		caches.append((W, b, z, A))
	WL = variables['W' + str(L)]
	bL = variables['b' + str(L)]
	zL = np.dot(WL, A) + bL
	AL = sigmoid(zL)
	caches.append((WL, bL, zL, AL))
	return AL, caches

def compute_cost(AL, Y):
	cost = np.mean(np.multiply(-np.log(AL), Y) + np.multiply(-np.log(1 - AL), 1 - Y))
	cost = np.squeeze(cost)
	return cost

def relu_back(A):
	return np.int64(A > 0)

def bp(AL, Y, caches):
	"""
        desc:
            反向传播，计算导数
        parameters:
            AL: 前向传播得到的结果
            Y: 真实值
            caches: 前向传播过程中缓存的数据
        return:
            gradients: 反向传播的导数
    """
	m = Y.shape[1]
	L = len(caches) - 1
	prev_AL = caches[L - 1][3]
	dzL = 1. / m * (AL - Y)
	dWL = np.dot(dzL, prev_AL.T)
	dbL = np.sum(dzL, axis = 1, keepdims = True)
	gradients = {'dW' + str(L) : dWL, 'db' + str(L) : dbL}
	for i in reversed(range(1, L)):
		post_W = caches[i + 1][0]
		dz = dzL
		dal = np.dot(post_W.T, dz)
		#Al = caches[i][3]
		#dzl = np.multiply(dal, relu_back(Al))
		#使用Al和zl效果相同

		zl = caches[i][2]
		dzl = np.multiply(dal, relu_back(zl))

		prev_A = caches[i -1][3]
		dwl = np.dot(dzl, prev_A.T)
		dbl = np.sum(dzl, axis = 1, keepdims = True)

		gradients['dW' + str(i)] = dwl
		gradients['db' + str(i)] = dbl
		dzL = dzl
	return gradients

def update_param(variables, gradients, learning_rate):
	L = len(variables) // 2
	for i in range(L):
		variables['W' + str(i + 1)] -= learning_rate * gradients['dW' + str(i + 1)]
		variables['b' + str(i + 1)] -= learning_rate * gradients['db' + str(i + 1)]
	return variables

def L_layer_model(X, Y, layers, learning_rate, maxCycles):
	costs = []
	variables = init_variables(layers)
	for i in range(maxCycles):
		AL, caches = fp(X, variables)
		cost = compute_cost(AL, Y)
		if i % 1000 == 0:
			print('Cost after iteration {} : {}'.format(i, cost))
			costs.append(cost)
		gradients = bp(AL, Y, caches)
		variables = update_param(variables, gradients, learning_rate)
	plt.clf()
	plt.plot(costs)
	plt.xlabel('iterations')
	plt.ylabel('cost')
	plt.show()
	return variables

def predict(X_test,y_test,variables):
	m = y_test.shape[1]
	Y_prediction = np.zeros((1, m))
	prob, caches = fp(X_test, variables)
	for i in range(prob.shape[1]):
		# Convert probabilities A[0,i] to actual predictions p[0,i]
		if prob[0, i] > 0.5:
			Y_prediction[0, i] = 1
		else:
			Y_prediction[0, i] = 0
	accuracy = 1- np.mean(np.abs(Y_prediction - y_test))
	return accuracy

def DNN(X_train, y_train, X_test, y_test, layers, learning_rate= 0.01, num_iterations=40000):
	variables = L_layer_model(X_train, y_train, layers, learning_rate, num_iterations)
	accuracy = predict(X_test,y_test,variables)
	return accuracy

if __name__ == "__main__":
	X_data, y_data = load_breast_cancer(return_X_y=True)
	X_train, X_test,y_train,y_test = train_test_split(X_data, y_data, train_size=0.8)
	X_train = X_train.T
	y_train = y_train.reshape(y_train.shape[0], -1).T
	X_test = X_test.T
	y_test = y_test.reshape(y_test.shape[0], -1).T
	accuracy = DNN(X_train,y_train,X_test,y_test,[X_train.shape[0],20, 20, 10, 5, 1])
	print('accuracy reaches %.4f' % accuracy)
