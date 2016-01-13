#!/usr/bin/env python
# coding=utf-8

import jieba
from sklearn import feature_extraction


def getWordCount():

    fr = open("./train_clean.txt")
    wordCount = {}
    for line in fr:
        words = line.split(" ")
        for word in words:
            if len(word)>1:
                wordCount[word] = wordCount.get(word,0)+1
    return wordCount


if __name__=='__main__':
    wd=getWordCount()
    for k,v in wd.items():
        print k,v
