#!/usr/bin/env python
# coding=utf-8


import jieba
import sys
import re
import codecs
import pickle
import numpy as np
from sklearn.externals import joblib



reload(sys)
sys.setdefaultencoding('utf-8')

class JD_extractor():
    """ 直接利用规则进行抽取相关所需信息 """
    """ 利用训练好的gbdt 分类器 判断一个句子是否为岗位要求 """

    def __init__(self):
        self.degreedic = [line.strip() for line in open('./data/degrees.txt')] # 载入学历词库
        self.majordic = [line.strip() for line in open('./data/majordic.txt')] # 载入专业词库
        self.w2vdict = pickle.load(open('./data/word2vec_dict.pkl'))
        self.linelist = []
        self.skills = [line.strip() for line in open('./data/skills.txt')]
        self.stoplist = [line.strip() for line in open('./data/full_stopwords.txt')]
        self.result = {} # 存储解析结果

    # 分句
    def cutlines(self,string):
        linelist = re.split(u'[。；？！\r\n]',string.strip())
        self.linelist =  [line.strip() for line in linelist if len(line)>2]
        return self.linelist

    # 切词
    def cutwords(self,sent):
        wlist = jieba.cut(sent)
        wlist =[w for w in wlist if  w not in self.stoplist]
        return wlist

    # 将句子分词后转化为词向量再相加，转化为句子向量
    def sent2vec(self,sent):
        sentvec = np.zeros(50)
        cnt = 1
        for word in self.cutwords(sent):
            if self.w2vdict.get(word,-1)!=-1:
                sentvec += self.w2vdict[word]
                cnt+=1.0
        sentvec = sentvec/cnt
        return np.ndarray.tolist(sentvec)


    # 抽取性别要求
    def regular_sex(self):
        sexvalue = 0
        sexdic = {0:u"男女不限",1:u"男",2:u"女"}
        for item in self.linelist:
            if re.search(u'[男女]|性别',item):
                if item.find(u'性别不限')!=-1:
                    sexvalue = 0
                    break
                elif item.find(u'男')!=-1:
                    if item.find(u'女')!=-1:
                        sexvalue= 0
                    else:
                        sexvalue=1
                    break
                elif item.find(u'女') != -1:
                    sexvalue=2
                    break    
        return sexdic[sexvalue]


    # 抽取年龄要求
    def regular_age(self):
        num =[]
        minage,maxage="null","null"
        for item in self.linelist:
            if re.search(u'岁|年龄',item):
                num = re.findall(u'\d{2,3}',item)
                num = [int(x) for x in num]
                if len(num)>=2:
                    maxage = min(max(num),100)
                    minage = max(min(num),0)
                elif len(num)==1:
                    if item.find(u'以上')!=-1:
                        minage,maxage = num[0],100
                    else:
                        minage,maxage = 0,num[0]
        return str(minage)+"-"+str(maxage)


    # 抽取专业要求
    def regular_major(self):
        for item in self.linelist:
            if item.find(u'专业')!=-1:
                for majorword in jieba.cut(item):
                    if majorword in self.majordic:
                        return majorword
        return "专业不限"


    # 抽取学历要求
    def regular_degree(self):
        for item in self.linelist:
            if re.search(u'学历|学位|大学|本科|研究生|专科|大专|要求',item):
                for degreeword in jieba.cut(item):
                    if degreeword in self.degreedic:
                        return degreeword
        return "学历不限"


    # 抽取工作经验年限要求    
    def regular_exp(self):
        yeardic = {u'半':0.5,u'一':1,u'二':2,u'两':2,u'三':3,u'四':4,u'五':5,u'六':6,u'七':7,u'八':8,u'九':9,u'十':10}
        zhyear = u'[一二三四五六七八九十两]'
        for item in self.linelist:
            pos = item.find(u'经验',0)
            if pos!=-1:
                item = item[max(0,pos-4):min(pos+5,len(item))]
                if re.findall(r'\d',item)!=None:
                    return re.findall(r'\d{1,2}',item)[0]
            else:
                if re.search(u"年以上",item):
                    pos = item.find(u"年以上")
                    return yeardic.get(item[pos-1:pos],0)
                elif re.search(zhyear,item):
                    return yeardic[re.search(zhyear,item).group(0)]
        return 0 



    # 利用训练好的分类器，抽取其他职责要求    
    def regular_req(self):
        reqstr = "" 
        clf = joblib.load('./output/gbdt_clf.model')
        for line in self.linelist:
            if re.search(u"公司介绍|职位描述|发布时间|",line) and len(line)<6:
                continue
            sentvec = self.sent2vec(line) 
            if clf.predict(sentvec)==1:
                reqstr += line+"\n"
            else:
                print line
        return reqstr



    # 利用技能词库抽取相关技能
    def regular_skill(self):
        skill = []
        for line in self.linelist:
            wordslist = self.cutwords(line)
            for w in wordslist:
                if w in self.skills:
                    skill.append(w)
        return " / ".join(skill) 

    # 薪酬
    def regular_pay(self):
        jdstr = ' '.join(self.linelist)
        pay = ""
        findpay =  re.findall(r'\d{1,2}k',jdstr)
        if len(findpay)==2:
            pay = '-'.join(findpay)
        elif len(findpay)==1:
            pay = str(findpay)+'以上'
        elif len(pay)>2:
            pay = findpay[0]+findpay[1]

        return pay

        

    def extr_info(self,inputstr):
        self.cutlines(inputstr)
        result = {}
        result["sex"] =self.regular_sex()
        result["age"] = self.regular_age()
        result["major"] = self.regular_major()
        result["degree"] = self.regular_degree()
        result["exp"] = self.regular_exp()
        result["skill"] = self.regular_skill()
        result["pay"] = self.regular_pay()
        if self.regular_req()!=0:
            result["req"] = self.regular_req()

        return result
   
        
    

if __name__ == "__main__":
    jdset= [] 
    jd = ""
    with codecs.open('./jd_test_input.txt','r','utf-8') as fr:
        for line in fr:
            if len(line)>1:
                if not line.startswith("==="):
                    jd+= line
                else:
                    jdset.append(jd)
                    jd = ""
    
    for jd in jdset:
        print "origin :\n",jd
        test = JD_extractor()
        result = test.extr_info(jd)
        for k,v in result.items():
            if v!="":
                print "{}:{}".format(k,v)
        print "\n"+"==="+"\n\n"



