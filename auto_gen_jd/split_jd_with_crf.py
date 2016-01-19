#!/usr/bin/env python
# coding=utf-8

import re
import codecs
import sys
import jieba
from itertools import chain
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelBinarizer
import pycrfsuite
# from mypreproces import Preprocess

sys.path.append('./crfsuite-0.12/example')

reload(sys)
sys.setdefaultencoding("utf-8")


class SplitJD(object):

    def __init__(self):
        self.SPLIT_LINE = re.compile(ur'[\r\t\n：:。]')
        self.CLEAN = re.compile(ur'[^\u4e00-\u9f5a\w]')
    
    
    def split_lines(self,fname='./data/jd_train.txt'):
        jdstr = codecs.open(fname).read() 
        resultlist = [line.strip() for line in  self.SPLIT_LINE.split(jdstr) if len(line)>1]
        
        print "length",len(resultlist)
        
        with codecs.open(fname[:-3]+'clean','w','utf-8') as fw:
            for line in resultlist:
                fw.write(line+'\n')
       
        return resultlist
    
    def read_iterfile(self,fname='./output/jd_train.clean'):
        res = []
        for line in codecs.open(fname,'r','utf-8'):
            line = line.strip()
            if len(line)<1 and len(res)>0:
                yield res
                res = []
            else:
                res.append(line)
        if len(res)>0:
            yield res


    def load_train_data(self,fname='./output/jd_train.clean'):
        res = []
        for i,jd in enumerate(self.read_iterfile(fname)):
            print " %dth,%s" %(i,jd[0])
            tmp = [(line.split('\t')) for line in jd if len(line.split('\t'))==2]
            if len(tmp)>2:
                res.append(tmp)           
            else:
                print 'len tmp',len(tmp)
        print "res %d jds" % len(res)
        return res
    
    

    def get_test_sents(self,fname='./train_req.txt'):
        sents = []
        tmpline = []
        for line in codecs.open(fname,"rb","utf-8"):
            if line!= '\n':
                tmpline.append(tuple(line.strip().split()))
            else:
                sents.append(tmpline)
                tmpline=[]
        return sents

    def isTips(self,word):
        lines = [line.strip() for line in codecs.open('./data/all_tips.txt')]
        findtip = re.search('|'.join(lines),word)
        if findtip:
            return findtip.group()
        else:
            return "None"


    def word2features(self,sent,i):
        word = sent[i][1]

        features = [
            "bias",
            "word[:3]="+''.join(list(jieba.cut(word))[0:3]),
            "word[:3]="+''.join(list(jieba.cut(word))[-3:]),
            "len="+str(len(word)),
            "startswithNum="+"1" if re.match("^\d+",word) else "-1",
            "idtagTips="+self.isTips(word),
            "hascompany="+"inc_name" if re.search("\S+公司",word) else "None",
            "hasNumbers=" + str(len(re.findall("\d+",word)))
        ]

        if i>0:
            word1 = sent[i-1][1]
            features.extend([
            "-1:word[:3]="+''.join(list(jieba.cut(word1))[0:3]),
            "-1:word[:3]="+''.join(list(jieba.cut(word1))[-3:]),
            "-1:len="+str(len(word1)),
            "-1:startswithNum="+"1" if re.match("^\d+",word) else "-1",
            "-1:istagTips="+self.isTips(word1)
            ])
        else:
            features.append('BOS')
        
        if i < len(sent)-1:
            word1 = sent[i+1][1]
            features.extend([
            "+1:word1[:3]="+''.join(list(jieba.cut(word1))[0:3]),
            "+1:word1[:3]="+''.join(list(jieba.cut(word1))[-3:]),
            "+1:len="+str(len(word1)),
            "+1:startswithNum="+"1" if re.match("^\d+",word) else "-1",
            "+1:istagTips="+ self.isTips(word1)            
            ])
        else:
            features.append('EOS')

        return features



    def sent2features(self,sent):
        return [self.word2features(sent,i) for i in range(len(sent))]

    def sent2labels(self,sent):
        return [label.encode('utf-8') for label,token in sent]

    def sent2tokens(self,sent):
        return [token for label,token in sent]


    def bio_classification_report(self,y_true,y_pred):
        lb = LabelBinarizer()

        y_true_combined = lb.fit_transform(list(chain.from_iterable(y_true)))
        y_pred_combined = lb.fit_transform(list(chain.from_iterable(y_pred)))
        
        tagset = set(lb.classes_)
        tagset = sorted(tagset,key = lambda tag:tag.split('-',1)[::-1])
        
        print 'tag'," | ".join(tagset),'\n\n'
        class_indices = {cls:idx for idx ,cls in enumerate(lb.classes_)}

        return classification_report(
            y_true_combined,
            y_pred_combined,
            labels = [class_indices[cls] for cls in tagset],
            target_names = tagset,
            )

    def train_crf(self):
        train_sents = self.load_train_data()[:-1]
        x_train = [self.sent2features(s) for s in train_sents ]
        y_train = [ self.sent2labels(s) for s in train_sents ]
        
        trainer = pycrfsuite.Trainer()      
        
        for xseq,yseq in zip(x_train,y_train):
           trainer.append(xseq,yseq)

        trainer.set_params({
            'c1':1.0,
            'c2':1e-3,
            'max_iterations':50,
            'feature.possible_transitions':True
        })
        
        trainer.select('l2sgd')
        trainer.train('./output/jd_split.model')


        
    def predict(self,fname,sent):
        tagger = pycrfsuite.Tagger()
        tagger.open(fname)

        pred = tagger.tag(self.sent2features(sent))
        correct = self.sent2labels(sent)

        errors = [ 0 if pred[i]==correct[i] else 1 for i in range(len(pred)) ]

        print "P1 percent %.3f" % (1.0-float(sum(errors))/len(pred))
        return pred


    def get_jd(self,sents):
        res = []
        tmp = []
        for line in sents:
            if line[0].startswith("B-BASIC") and len(tmp)>0:
                res.append(tmp)
                tmp.append(line[1])
            else:
                tmp.append(line[1])
        if len(tmp)>0:
            res.append(tmp)
        return res



def main():
    test = SplitJD()
    

   # test.train_crf()
    example_sent = [line.strip() for line in codecs.open('./data/jd_text.txt')]
    pred = test.predict(fname="./data/jd_split.model",sent=example_sent)
   

    sents = zip(pred,example_sent)

    jds = test.get_jd(sents)
    print "len jds",len(jds)

    print "jd1",'\n'.join(jds[0])
    print "done"
    # print test.bio_classification_report(y_test,y_pred)


if __name__ == "__main__":
    main()
