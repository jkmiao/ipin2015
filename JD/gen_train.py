#!/usr/bin/env python
# coding=utf-8


import myword2vec
import numpy as np

class gen_train():
    __init__(self):
        self.w2v = myword2vec.Word2vec()
        self.w2v_dic = myword2vec.load_word_vector('./vectors_60.bin',60)

    # 生成符合liblinear训练集格式的负例,是公司简介,不是招聘描述
    def gen_neg_train(self,fileName):
        # filename='./inc_intro.json'
        outFile = open('Inc2vec.txt','w')
        load = myword2vec.load_json(fileName)
        dataList = load.getData('inc_description')
        for data in dataList:
            for line in self.w2v.word_split(data):
                w2v_para = np.zeros((1,50))
                wlist = self.w2v.cut_words(line)
                w2vlist = self.w2v.wordtovec(wlist,w2vdic)
                for vec in w2vlist:
                    w2v_para += np.array(vec)
                outFile.write('-1'+' ')
                i=1
                for num in w2v_para[0]:
                    outFile.write(str(i)+':'+str(num)+' ')
                    i+=1
                outFile.write('\n')
        outFile.close()
