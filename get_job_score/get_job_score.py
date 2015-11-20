#!/usr/bin/env python
# coding=utf-8

import sys
import csv
import json,jieba
from collections import OrderedDict
reload(sys)
sys.setdefaultencoding('utf-8')


# jieba.load_userdict('./data/jobname.txt')
jieba.initialize()


def load_data(fname="./data/ci_zhiji.csv"):
    reader = csv.reader(open(fname))
    res = {}
    for line in reader:
        if reader.line_num == 1:
            continue
        field,jobname,score = line[0],line[1],line[2]
        print 'jobname',field,jobname
        if field not in res:
            res[field] = {}
        else:
            res[field][jobname] = float(score)

    json.dump(res,open('./data/jobscore_database.json','wb'))
    return res

def load_domain(fname='./data/ind.csv'):
    reader = csv.reader(open(fname))
    res = OrderedDict()
    for line in reader:
        if reader.line_num ==1:
            continue
        res[line[0]]=line[1]
    return res
    json.dump(res,open('./data/domain_dict.json','wb'))
        
def strQ2B(ustring):
    """
    中文全角转半角
    """
    res = ""
    for uchar in ustring:
        c = ord(uchar)
        if c == 0x3000:
            c = 0x2000
        else:
            c -= 0xfee0
        if c<0x0020 or c>0x7e:
            c += 0xfee0
        res += unichr(c)
    return res


def leven_distance(s1,s2):
    """
    动态规划实现编辑距离
    """
    m,n = len(s1),len(s2)
    colsize,v1,v2 = m+1,[],[]

    for i in range(n+1):
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
            minValue = min(minValue,v2[j-1]+1)
            minValue = min(minValue,v1[j-1]+cost)
            v2[j] = minValue
        for j in range(n+1):
            v1[j] = v2[j]
    return v2[n]
                

class GenJobScore(object):
    def __init__(self):
        self.jobscore_db = json.load(open('./data/jobscore_database.json'))
        self.domain_dict = load_domain()

    def cal_job_score(self,jobname='ＰＨＰpython工程师',domain='计算机'):
        jobname = strQ2B(jobname.decode('utf-8')).lower()
        domain = strQ2B(domain.decode('utf-8')).lower()
        domain = self.get_top_domain(domain,self.jobscore_db.keys())
        cnt,score = 0,0
        for word in jieba.cut(jobname):
            if word in self.jobscore_db[domain]:
                score += self.jobscore_db[domain][word]
                cnt += 1
        if cnt==0:
            cnt = 1
        print 'score',score,cnt
        rank = "%.2f" %(float(score)/cnt/1000)

        if float(rank)>10:
            rank = 10
        return str(rank)

    def get_top_domain(self,domain,namelist):
        dis = [(leven_distance(domain,other),other) for other in namelist ]
        dis.sort()

        for k in dis[:5]:
            print 'dis',k[1],k[0]

        return dis[0][1]



if __name__ == "__main__":
    test = GenJobScore()
    domain = sys.argv[1]
    jobname = sys.argv[2]
    rank = test.cal_job_score(domain=domain,jobname=jobname)
    print 'rank',rank
