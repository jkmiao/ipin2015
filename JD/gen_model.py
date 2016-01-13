#!/usr/bin/env python
# coding=utf-8

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.externals import joblib
from sklearn.metrics import roc_auc_score
from sklearn.cross_validation import train_test_split
import random
import pickle


def loadTrain(fname="data/trainData.pkl"):
    fr = open(fname)
    fr = pickle.load(fr)
    data = [line for line in fr]
    data = random.sample(data,2000)
    X = []
    y = []
    for line in data:
        lineArr = []
        curLine = line.strip().split()
        for i in range(1,len(curLine)):
            lineArr.append(float(curLine[i]))
        X.append(lineArr)
        y.append(int(curLine[0]))
    return X,y


def lr_clf(x_train,x_test,y_train,y_test):
    clf = LogisticRegression()
    clf.fit(x_train,y_train)
    scores = clf.score(x_test,y_test)
    print "lr_clf scores: ",scores
    joblib.dump(clf,'./output/lr_clf.model')


def gbdt_clf(x_train,x_test,y_train,y_test):
    clf = GradientBoostingClassifier(n_estimators=100)
    clf.fit(x_train,y_train)
    y_pred = clf.predict_proba(x_test)[:,1]
    print "gbdt F1 scores",clf.score(x_test,y_test)
    scores = roc_auc_score(y_test,y_pred)
    print "gbdt_clf scores: ",scores
    joblib.dump(clf,'./output/gbdt_clf.model')
  

def svm_clf(x_train,x_test,y_train,y_test):
    clf = LinearSVC()
    clf.fit(x_train,y_train)
    print "F1 scores",clf.score(x_test,y_test)
    joblib.dump(clf,"./output/svm_clf.model")


def gen_model():
    X,y = loadTrain()
    print "loaded data"
    x_train,x_test,y_train,y_test = train_test_split(X,y,test_size=0.3,random_state=28)
    print "modeling lr..."
    lr_clf(x_train,x_test,y_train,y_test)
    print "modeling gbdt..."
    gbdt_clf(x_train,x_train,y_train,y_train)
    print "modeling svm..."
    svm_clf(x_train,x_test,y_train,y_test)

    


if __name__ == "__main__":
    print "start>>>"
    gen_model()
    print "done"
