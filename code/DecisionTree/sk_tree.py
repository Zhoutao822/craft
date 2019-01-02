#coding=utf-8
# ==============================================================================
"""使用sklearn实现决策树
版本：
    Python：3.6.7
参考：
    https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier
"""
#%%
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn import tree

raw_data = load_wine()
x_train, x_test, y_train, y_test = train_test_split(
    raw_data.data, raw_data.target, test_size=0.2, random_state=2019)
clf = tree.DecisionTreeClassifier(criterion='entropy')
clf.fit(x_train, y_train)

print('测试集准确率：{:.4f}'.format(clf.score(x_test, y_test)))

