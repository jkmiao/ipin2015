#!/usr/bin/env python
# coding=utf-8

__author__='jkmiao'

import jieba
from sklearn.cluster import KMeans
from gensim import corpora,models
import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def strQ2B(ustring):
    """
    中文全角转半角
    """
    res = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:
            inside_code = 32
        elif inside_code >=65281 and inside_code <= 65374:
            inside_code -= 65248

        res += unichr(inside_code)
    return res


def leven_distance(s1,s2):
    """
    动态规划实现编辑距离
    """

    s1 = strQ2B(s1.decode('utf-8')).lower()
    s2 = strQ2B(s2.decode('utf-8')).lower()

    m,n = len(s1),len(s2)
    colsize,v1,v2 = m+1,[],[]

    for i in range((n+1)):
        v1.append(i)
        v2.append(i)

    for i in range(m+1)[1:m+1]:
        for j in range(n+1)[1:n+1]:
            cost = 0
            if s1[i-1]==s2[j-1]:
                cost = 0
            else:
                cost = 1
            minValue = v1[j]+1
            if minValue > v2[j-1]+1:
                minValue = v2[j-1]+1
            if minValue >v1[j-1]+cost:
                minValue = v1[j-1]+cost
            v2[j] = minValue
        for j in range(n+1):
            v1[j] = v2[j]

    return v2[n]

class Mycluster():
    def __init__(self):
        self.dictionary = {}
        self.corpus = []
        self.tfidf = []

    def gen_corpus(self,documents):
        texts = [ [w for w in jieba.cut(doc) if len(w)>1] for doc in documents ]
        self.dictionary = corpora.Dictionary(texts)
        self.corpus = [self.dictionary.doc2bow(text) for text in texts ]
        self.tfidf = models.TfidfModel(self.corpus)
    
    def line2vec(self,line):
        vec = [word for word in self.dictionary.doc2bow(jieba.cut(line)) if len(word)>1]
        vec = self.tfidf[vec]
        res = [.0] * len(self.dictionary)
        for w in vec:
            res[w[0]] = w[1]
        return res



    def get_closet(self,center,linelist):
        dis = [ (self.sim_cosine(center,self.line2vec(other)),other) for other in linelist ]
        dis.sort()
        return dis[0][1]

    def sim_cosine(self,vec1,vec2):
        assert len(vec1)==len(vec2),"vec1=%d and vec2=%d, must have the same lenght "%(len(vec1),len(vec2))
        num = np.sum(w[0]*w[1] for w in zip(vec1,vec2))
        denom = np.linalg.norm(vec1)*np.linalg.norm(vec2)
        cos = num/denom
        sim = 0.5+0.5*cos
        return sim


    def kcluster(self,texts,k=5):
        self.gen_corpus(texts)
        data = [self.line2vec(line) for line in texts]

        km =KMeans(n_clusters=k+2 if k+2<len(data) else len(data),init="k-means++",max_iter=100,n_init=2)
        km.fit(data)
        labels = km.labels_
        
        label_dict = {}
        label_center = {}
        
        for label,line in zip(labels,texts):
            if label not in label_dict:
                label_dict[label] = [line]
            else:
                label_dict[label].append(line)

        for label,line in zip(labels,data):
            if label not in label_center:
                label_center[label] = np.array(line)
            else:
                label_center[label] += np.array(line)

        for label in label_center:
            label_center[label] = label_center[label]/len(label_dict[label])

        # 标注好聚类的句子，按聚类大小排序
        label_linlist = sorted(label_dict.iteritems(),key=lambda x:len(x[1]),reverse=True)
        res = []
        for label_line in label_linlist:
            line = self.get_closet(label_center[label_line[0]],label_dict[label_line[0]])
            res.append(line)
        return res[:k]


if __name__=="__main__":
    s = sys.argv[1]
    print strQ2B(s)
    texts=["1、拓展和维护客户，完成销售任务；",
           "2、负责BI产品销售，完成每月公司交办的客户拓展数量及相应的销售量；",
           "3、持续更新合作客户的案例信息。,信息",
           "3-5年软件行业销售/售前经验；",
           "拓展和维护客户，完成销售任务，任务；",
           "2、负责BI产品销售，完成每月公司交办的客户拓展数量及相应的销售量，完成每月公司交办的客户拓展数量及相应的销售量",
           "3、持续更新合作客户的案例信息"]
    test = Mycluster()
    res = test.kcluster(texts,3)

    print '\n'.join(res)
