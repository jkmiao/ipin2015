#!/usr/bin/env python
# coding=utf-8

import sys,re
from simhash import Simhash
from copy import deepcopy
from collections import defaultdict
from jd_parser import JdParser
reload(sys)
sys.setdefaultencoding("utf-8")


class Evaluate(object):
    """
    对最后jd结果进行评测
    """
    def __init__(self):
        self.LABELLIST = ["job_name","job_tag","sex","age","degree","major","exp","pay","skill","duty","demand","inc_name","inc_tag","benefits","pub_time","end_time","cert","workplace","other"]

    def cal_dist(self,stra,strb):
        return Simhash(stra.strip()).distance(Simhash(strb.strip()))

    def evaluate_single(self,dicta,dictb):
        res = defaultdict(int)
        both_keys = set(dicta.keys()) | set(dictb.keys())
#        print "len both_keys",len(both_keys),' / '.join(both_keys)
        for key in both_keys:
            try:
                if self.cal_dist(dicta[key],dictb[key])<5:
                    res[key] = 1
                else:
                    res[key] = 0
                    print "==="*20
                    print "error",key
                    print "reference",dicta[key]
                    print 'output',dictb[key]
                    print "==="*20
            except Exception,e:
                print e
                continue
        return res

    def evaluate(self,tagged_jd,output_jd):
        assert len(tagged_jd)==len(output_jd),"list must have the same length, %d,%d" %(len(tagged_jd),len(output_jd))
        cal_res = []
        for jd in zip(tagged_jd,output_jd):
            tmp = self.evaluate_single(jd[0],jd[1])
            cal_res.append(deepcopy(tmp))

        res = defaultdict(lambda :defaultdict(float))
        for jd in cal_res:
            for key in jd:
                res[key]["precision"]+=jd[key]
                res[key]["count"] += 1
        for key in res:
            res[key]["precision"] /= res[key]["count"]
            res[key]['precision'] = "%3.1f%%" %(res[key]['precision']*100)
        return res


    def isLabel(self,label):
        if label in self.LABELLIST:
            return True
        return False

    def read_test_iter(self,fname="./data/lagou_test.txt"):
        res = {}
        block = []
        LABEL = re.compile(u'^[a-z_]{3,10}')
        label = "job_name"
        for line in open(fname):
            if line.startswith(u"=====") and len(res)>0:
                yield res
                block = []
                res.clear()
            elif LABEL.search(line) and self.isLabel(LABEL.match(line.strip()).group()): 
                res[label] = '\n'.join(block)
                block = []
                label = LABEL.match(line.strip()).group()
                continue
            else:
                block.append(line.strip())
        
        if block:
            res[label] ='\n'.join(block)
        if res:
            yield res

    
    def read_train_iter(self,fname='./data/lagou_train.txt'):
        """
        读入测试数据，31份JD
        """
        res = []
        for line in open(fname):
            if line.startswith(u"====") and len(res)>0:
                yield '\n'.join(res)
                res = []
            elif len(line.strip())>2:
                res.append(line.strip())
        if res:
            yield '\n'.join(res)


    def clean_data():
        line = [line.strip() for line in open('./data/lagou_test.txt') if len(line.strip())>2]
        jdstr = '\n'.join(line)
        jdstr = re.sub(" : ","\n",jdstr)
        open('./data/lagou_test_txt.clean','wb').write(jdstr+"\n")



    def load_test_data(self,fname='./data/lagou_train.txt',testfame='./data/lagou_test.txt'):
        test = []
        for i,jd in enumerate(self.read_test_iter(fname='./data/lagou_test.txt')):
            test.append(deepcopy(jd))
        return test



    def get_output_data(self,jd_parser,fname='./data/lagou_train.txt'):
        res = []
        for jdstr in self.read_train_iter(fname):
            single_res = jd_parser.parser(jdstr.decode('utf-8'))
            res.append(deepcopy(single_res))
        return res




if __name__ == "__main__":
    test = Evaluate()
    jdparser = JdParser()
    input = test.load_test_data()
    output = test.get_output_data(jdparser)
    res = test.evaluate(input,output)
    for k in res:
        print k,res[k]









