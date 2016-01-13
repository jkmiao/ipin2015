#!/usr/bin/env python
# coding=utf-8

import re,codecs,jieba
from tgrocery import Grocery 
import numpy as np
from util import lcs_len
import sys,os
reload(sys)

sys.setdefaultencoding("utf-8")




base_dir =  os.path.split(os.path.realpath(__file__))[0]
print base_dir
sys.path.append(base_dir)

class JdParserTop(object):


    def __init__(self):
        self.CLEAN_TEXT = re.compile(u"[^\u4e00-\u9fa5\w\d；:：;,。、\.，。！!@（）\r\n\(\)\-\+ －　]")
        
        self.clf = Grocery(base_dir+"/jdclf")
        self.clf.load()
        
#        self.clf = joblib.load('./data/jd_clf.model')
#        self.w2v = models.Word2Vec.load("./data/jdw2v_50.bin")

        self.SPLIT_LINE = re.compile(u"[\r\n；:：。！？;]|[　\s \xa0\u724b]{4,}")
        self.CLEAN_LINE = re.compile(u"^[\u2022（【\[\s\t\r\n\(\- 　]?[\da-z１２３４５７８９]{1,2}[\.,。、，：:）】\]\)\s]|^[！＠＃￥％……＆×（）\(\)｛｝：“｜、－\-，。：:\.]|^[一二三四五六七八九１２３４５６７８９\d]{0,2}[\.、\s:：　]|[，；。、\s　\.]$|^[\s　\u2022 \uff0d \u25cf]")
        self.CLEAN_JOBNAME = re.compile(u"急聘|诚聘|高薪|包[食住宿餐]|.险一金|待遇|^急?招")

        self.PAY = re.compile("(\d{3,}\-)?\d{3,}元")
        self.SEX = re.compile(u"性别|男|女")
        self.AGE = re.compile(u"\d+周?岁|年龄")
        self.JOB_TAG = re.compile(u"全职|实习")

        self.START_DEMAND = re.compile(u"(任职资格|岗位要求|工作要求|任职条件|任职要求|职位要求)[：:\s】\n　]?")
        self.START_DUTY = re.compile(u"(工作内容|岗位职责|工作职责|职位描述|工作描述|职位介绍|职位职责|岗位描述)[:：\s 】\n　]")
        self.START_BENEFIT = re.compile(u"(福利待遇|待遇|福利)[:：\s\n】]")
        
        self.INC_URL = re.compile(u"(网.|官.?网.?).{0,3}[\w\d_/\.:\-]+")
        self.DEMAND = re.compile(u"精通|熟悉|熟练|有.+经验")
        self.DUTY = re.compile(u"负责|促成|为客户|安排的其.工作")
        self.BENEFIT = re.compile(u".险一金|福利|晋身|休假|带薪|补助|补贴")
        self.CERT = re.compile(u"(\S{2,8}证书|CET-\d|普通话|英语|口语|.语|日文|雅思|托福|托业)(至少)?(通过)?[\d一二三四五六七八九]级[及或]?(以上)?|(英语)?CET-\d级?(以上)?|\
                                 医学.{0,3}证|会计.{0,3}证|律师.{0,3}证|有.{1,8}证书")


        
        self.degreedic = set([line.strip() for line in codecs.open(base_dir+'/data/degrees.txt','rb','utf-8')])
        self.majordic = set([line.strip() for line in codecs.open(base_dir+'/data/majordic.txt','rb','utf-8')])
        self.skilldic = set([line.strip() for line in codecs.open(base_dir+'/data/skills.txt','rb','utf-8')])
        self.jobdic = set([line.strip() for line in codecs.open(base_dir+'/data/jobnames.txt','rb','utf-8')])

        jieba.load_userdict(base_dir+'/data/majordic.txt')
        jieba.load_userdict(base_dir+'/data/skills.txt')
        jieba.load_userdict(base_dir+'/data/firm.txt')
        jieba.load_userdict(base_dir+'/data/degrees.txt')
        jieba.load_userdict(base_dir+'/data/benefits.txt')

    
    def clean_line(self,line):
        return self.CLEAN_LINE.sub("",line).strip()


    def line2vec(self,line):
        vec = np.zeros(50)
        for word in jieba.cut(line):
            if word in self.w2v.vocab:
                vec += self.w2v[word]

        return vec
    
    
    def clean_jobname(self,jobname):
        if jobname.lower() in self.jobdic:
            return jobname.lower()
        else:
           res = [(lcs_len(jobname,job),job) for job in self.jobdic]
           res.sort()
           return res[-1][1]

