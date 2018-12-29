#!/usr/bin/python3
#coding=utf-8
# ==============================================================================
"""使用sklearn实现决策树
版本：
    Python：3.6.7
参考：
    https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier
"""
#%%
from sklearn.datasets import load_wine, load_diabetes
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn import tree

rawData = load_wine()
X_train, X_test, y_train, y_test = train_test_split(rawData.data, rawData.target, test_size=0.2, random_state=2018)
clf = tree.DecisionTreeClassifier(criterion='entropy')
clf.fit(X_train, y_train)

print(clf.score(X_test, y_test))

