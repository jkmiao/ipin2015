#!/usr/bin/env python
# coding=utf-8

import jieba
from gensim import corpora,models
from collections import defaultdict
import cPickle as pickle
import random
import nltk,sys

class MyClassify(object):
    
    def __init__(self):
        self.dictionary = {}
        self.corpus = []
        self.wordlist = pickle.load(open('./wordlist.pkl'))


    def gen_dataset(self,documents):
        self.gen_corpus(documents)
        res = [self.doc2vec(doc) for doc in documents]
        return res

    def gen_corpus(self,documents):
        texts = [ list(jieba.cut(doc)) for doc in documents]
        self.dictionary = corpora.Dictionary(texts)
        self.corpus = [self.dictionary.doc2bow(text) for text in texts]
        self.tfidf = models.TfidfModel(self.corpus)

    def doc2vec(self,doc):
        vec = self.dictionary.doc2bow(jieba.cut(doc))
        vec = self.tfidf[vec]
        wordlist = [0] * len(self.dictionary)
        for w in vec:
            wordlist[w[0]] = w[1]
        return wordlist



def get_topk_word(fname='./whole_data.txt',k=2000):
    worddict = defaultdict(int)
    for i,line in enumerate(open(fname)):
        for word in jieba.cut(line):
            if len(word)>1:
                worddict[word] += 1
    res = sorted(worddict.iteritems(),key=lambda x:x[1],reverse=True)
    wordlist = [w[0] for w in res[:k]]
    pickle.dump(wordlist,open('./wordlist.pkl','wb'))
        
        
def doc2vec2(doc,wordlist):
    res = defaultdict(int)
    for word in jieba.cut(doc):
        if word in wordlist:
            res[word] +=1
    return res



def gen_cls():
    get_topk_word()
    wordlist = pickle.load(open('./wordlist.pkl','rb'))
    datasets = ([(doc2vec2(line,wordlist),'duty') for line in open('./duty.txt')]+\
                [(doc2vec2(line,wordlist),'demand') for line in open('./demand.txt')]+\
                [(doc2vec2(line,wordlist),'other') for line in open('./other.txt')])

    random.shuffle(datasets)
    num = len(datasets)/3
    train_set ,test_set = datasets[:2*num],datasets[2*num:]
    cls = nltk.NaiveBayesClassifier.train(train_set)
    pickle.dump(cls,open('nb_cls.pkl','wb'))






if __name__ == "__main__":
 #   gen_cls()
    wordlist = pickle.load(open('./wordlist.pkl','rb'))
    for w in wordlist[:200]:
        print w
    cls = pickle.load(open('nb_cls.pkl'))
    line = sys.argv[1]
    if not line:
       line = u'丰富的互联网前端开发经验, 熟练使用HTML、CSS、Javascript等前端语言制作网页页面' 
    input = doc2vec2(line,wordlist)
    print cls.classify(input)
    datasets = ([(doc2vec2(line,wordlist),'duty') for line in open('./duty.txt').readlines()[:2000]]+\
                [(doc2vec2(line,wordlist),'demand') for line in open('./demand.txt').readlines()[:2000]])

    random.shuffle(datasets)
    num = len(datasets)/3

    print nltk.classify.accuracy(cls,datasets[:num])

