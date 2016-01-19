#!/usr/bin/env python
# coding=utf-8

import jieba,re
from gensim import corpora,models
from sklearn.cluster import KMeans
import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class MyCorpus(object):
    def __init__(self,fname):
        self.fname = fname

    def __iter__(self):
        for line in open(self.fname):
            yield jieba.cut(line,cut_all=False)


class MyCluster(object):

    def __init__(self):
        self.CLEAN = re.compile(ur"[^\u4e00-\u9f5aA-Za-z0-9]")
        self.word2vec = models.Word2Vec.load('./data/jdw2v_50.bin')
        self.dictionary = {}
        self.corpus = []

    
    def gen_dataset(self,documents):
        self.gen_corpus(documents)
        res = [self.line2vec(doc) for doc in documents]
        return res


    def gen_corpus(self,documents):
        texts =[[ word for word in jieba.cut(doc) if len(word)>1] for doc in documents ]
        self.dictionary = corpora.Dictionary(texts)
        self.corpus = [self.dictionary.doc2bow(text) for text in texts]
        self.tfidf = models.TfidfModel(self.corpus)
    
    def sim_cosine(self,vec1,vec2):
        assert len(vec1)==len(vec2)," vec1=%d and vec2=%d must have the same length " %(len(vec1,len(vec2)))
        num = np.sum(w[0]*w[1] for w in zip(vec1,vec2))
        denom = np.linalg.norm(vec1)*np.linalg.norm(vec2)
        cos = num/denom
        sim = 0.5+0.5*cos
        return sim


    def line2vec(self,doc):
        vec =  self.dictionary.doc2bow([w for w in jieba.cut(doc) if len(w)>1])
        vec = self.tfidf[vec]
        wordlist = np.zeros(len(self.dictionary))
        for w in vec:
            wordlist[w[0]] = w[1]
        return wordlist
            
    def line2vec2(self,line):
        vec = np.zeros(50)
        for word in jieba.cut(line):
            if word in self.word2vec.vocab:
                vec += self.word2vec[word]
        return vec
            
    
    def get_closest(self,center,linelist):
        dis = [(self.sim_cosine(center,self.line2vec2(other)),other) for other in linelist]
        dis.sort()
        return dis[0][1]
    

    def kcluster(self,texts,k=3):
#        self.gen_dataset(texts)
        data = [self.line2vec2(line) for line in texts]
        # data = [ map(lambda x:round(x,5),line) for line in data ]
        km = KMeans(n_clusters= k+2 if k+2<len(data) else len(data),init='k-means++',max_iter=100,n_init=2)
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
                label_center[label] = line
            else:
                label_center[label] += line
        
        for label in label_center:
            label_center[label] = label_center[label]/len(label_dict[label])
        
        label_linelist = sorted(label_dict.iteritems(),key=lambda x:len(x[1]),reverse=True)
        res = []
        for label_line in label_linelist:
            line = self.get_closest(label_center[label_line[0]],label_dict[label_line[0]])
            res.append(line)
        return res[:k]


if __name__ == "__main__":
    texts = [ line.strip() for line in open('data/市场策划.txt') if len(line)>3]
    test = MyCluster()
    res = test.kcluster(texts,k=4)

    print '\n'.join(res)

