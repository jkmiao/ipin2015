#!/usr/bin/env python
# coding=utf-8

import jieba
import pickle
import codecs
import sys
import numpy as np
import re
import simplejson
import random
reload(sys)
sys.setdefaultencoding("utf-8")


class gen_train():
    def __init__(self):
        print "loading w2v dict..."
        self.w2vdict = pickle.load(open("./data/word2vec_dict.pkl"))
        self.stoplist = [word for word in open('./data/full_stopwords.txt').readlines() ]
    
    def load_json_data(self,fname=None,arg1=None,arg2=None):
        retData = []
        with codecs.open(fname,'r',"utf-8") as fr:
            for line in fr:
                try:
                    data = simplejson.loads(line)
                except Exception:
                    continue
                if arg2 == None:
                    if data.get(arg1,False) != False and len(data[arg1].strip())>2:
                        retData.append(data[arg1].strip())
                elif data.get(arg1,False)!=False and data[arg1].get(arg2,False)!=False:
                    if len(data[arg1][arg2])>2:
                        retData.append(data[arg1][arg2].strip())
        return retData


    def sent_split(self,string):
        P1 = re.compile(u"[。；？！\t\r\n]")
        lines = [line for line in P1.split(string) if len(line)>1]
        return lines


    def cutwords(self,sent):
        wordlist = [w for w in jieba.cut(sent) if w not in self.stoplist]
        return wordlist
        

    def sent2vec(self,sent):
        w_list = self.cutwords(sent)
        sentvec = np.zeros(50)
        count = 1
        for word in w_list:
            if self.w2vdict.get(word,-1)!=-1:
                sentvec += self.w2vdict[word]
                count += 1.0
        sentvec = sentvec/count
        sentvec = np.ndarray.tolist(sentvec)
        sentvec = map(str,sentvec)
        return sentvec


    def gen_inc_data(self,fname='../preprocess/data/inc_intro.json'):
        incdata = self.load_json_data(fname,arg1="inc_description")
        fw = codecs.open('../preprocess/output/miniinc_data.csv','w','utf-8')
        cnt = 1
        retData = []
        for data in incdata:
            for line in self.sent_split(data.strip()):
                sentvec = self.sent2vec(line)
                sentvec.insert(0,'-1')
                retData.append(sentvec)
                sentvec = " ".join(sentvec)
                fw.write(sentvec+"\n")
            cnt+=1
            if cnt%200==0: print cnt
        fw.close()
        return retData

        
    def gen_jd_data(self,fname='../preprocess/data/jd_100w_new.json'):
        jddata = self.load_json_data(fname,arg1="job",arg2="job_description")
        fw = codecs.open('../preprocess/output/jd_data.csv','w','utf-8')
        cnt=1
        retData = []
        for data in jddata:
            for line in self.sent_split(data.strip()):
                sentvec = self.sent2vec(line)
                sentvec.insert(0,'1')
                retData.append(sentvec)
                sentvec = " ".join(sentvec)
                fw.write(sentvec+"\n")
            cnt+=1
            if cnt%200==0: print cnt
        fw.close()
        return retData

    def gen_train_data(self):
        print "generating inc train data..."
        trainData = self.gen_inc_data()
        print "generating jd train data..."
        jd_data = self.gen_jd_data()
        for line in jd_data:
            trainData.append(line)
        random.shuffle(trainData)
        fw = open('./output/trainData.pkl','wb')
        pickle.dump(trainData,fw)

   

if __name__ == "__main__":
    test = gen_train()
    test.gen_train_data()
    print "done"
