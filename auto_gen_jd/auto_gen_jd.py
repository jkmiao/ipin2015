#!/usr/bin/env python
# coding=utf-8

import simplejson as json
import numpy as np
import re,sys,codecs
from simhash import Simhash
from util import strQ2B
from util import Mycluster
from collections import OrderedDict
import jieba
reload(sys)
sys.setdefaultencoding('utf-8')

jieba.load_userdict('./data/skills.txt')

class AutoGenJD(object):
    """
    自动生成ＪＤ职责、要求和技能
    """

    def __init__(self):
        self.CLEAR_NUM = re.compile(u"^[\(（【]?\d+[\)）\.】　、\s]")
        self.CLEAR_COLO = re.compile(u"^[，。、;\s\.\]（）【】\)]|[\.，。；：。]$|[\s\xa0]")
        self.jd_database = json.load(open("./data/jd_database.json"))
        self.skill_db = json.load(open('./data/jd_skills_db.json'))

        self.SKILL = re.compile(u"精通|熟悉|熟练|了解|掌握|善于|懂得|善于|擅长|能力|具有|具备|资格")
        self.NOTSKILL = re.compile(u"梦想|公司|具有以下条件|为人|应届生|积极|主动|生活|保证|一下条件|地址|待遇|福利|工作地.|工作时.")
        self.skill_words = [token.strip() for token in codecs.open('./data/skills.txt','rb','utf-8')]

     #   self.tk4sents = TextRank4Sentence(stop_words_file ='./data/stopword.data')
     #   self.tk4words = TextRank4Keyword(skill_words_file ='./data/skills.txt')

        self.km = Mycluster()

    def is_most_english(self,line):
        en_word = [ c for c in line if (c>=u'\u0041' and c<=u'\u005a') or (c>=u'\u0061' and c<=u'\u007a') ]

        return float(len(en_word))/len(line)>0.7


    def clear_jd(self,linelist):
        """
        清洗数据，去除句子前后的序号、数字、标点符号等
        """
        res = set()
        for line in linelist:
            if len(line)<5:continue
            if self.NOTSKILL.search(line):continue
            if self.is_most_english(line):continue
            line = self.CLEAR_NUM.sub("",line)
            line = self.CLEAR_COLO.sub("",line)
            res.add(line)
        return res
    
    def simhash_distance(self,job1,job2):
        job1 = strQ2B(job1.decode('utf-8')).lower()
        job2 = strQ2B(job2.decode('utf-8')).lower()
        return Simhash(job1).distance(Simhash(job2))
    

    def get_closet_jobname(self,jobname='java'):
        jobname = strQ2B(jobname).lower()
        dis = [ (self.simhash_distance(jobname,other),other) for other in self.jd_database.keys() ]
        sorted_jobname = sorted(dis,key = lambda x:x[0])

        for k,v in sorted_jobname[:5]:
            print 'jobname',k,v
        return sorted_jobname[0][1]

        
    def demand_score(self,line):
        s = len(line)+100
        if re.search(u"男|女|性别|岁|不限",line):
            s -= 60
        if re.search(u"学历|专业|\d+[kK元]",line):
            s -= 40
        if re.search(u"经验",line):
            s -= 20
        return s
                    

    def get_demand(self,jobname='python',num=6):
        """
        使用kmeans 聚类，相同一类只出现一句，排序后输出
        """
        jd_demand = self.clear_jd(self.jd_database[jobname]['demand'])
        jd_demand = filter(lambda x:not self.NOTSKILL.search(x),jd_demand)
        
        if len(jd_demand)<num:
            res = jd_demand
        else:
            res = self.km.kcluster(jd_demand,k=num)
        return sorted(res,cmp = lambda x,y:self.demand_score(x)-self.demand_score(y))


    def duty_score(self,line):
        s = len(line)+100
        if re.search(u"负责",line):
            s -= 20
        if re.search(u"参与",line):
            s -= 10
        if re.search(u"出差|外地",line):
            s += 10
        if re.search(u"交办的|其他|其它",line):
            s += 20
        return s

    def get_duty(self,jobname="python",num=4):
        """
        同理句子聚类后输出，每一类输出一句
        """
        jd_duty = self.clear_jd(self.jd_database[jobname]['duty'])
        if len(jd_duty)<num:
            res = jd_duty
        else:
            res = self.km.kcluster(jd_duty,k=num)
        return sorted(res,cmp = lambda x,y:self.duty_score(x)-self.duty_score(y))

    def get_skill(self,jobname="python",num=5):
        """
        从demand中关键词抽出相关技能短语
        """
        key_words = {}
        
        jd_skill = self.clear_jd(self.jd_database[jobname]['demand'])
        
        for line in jd_skill:
            for word in jieba.cut(line):
                word = strQ2B(word).lower()
                if word in self.skill_words:
                    key_words[word] = key_words.get(word,1)+1


        key_words = sorted(key_words.iteritems(),key=lambda x:x[1],reverse=True)
        
        res = [ w[0] for w in key_words[:int(num*np.log(num))]]
        
        print 'key_words:'
        print '\n'.join(res)

        for word in jieba.cut(jobname):
            word = strQ2B(word).lower()
            if word in self.skill_words and word not in res:
                res.insert(0,word)

        after_top3 = res[3:]
        np.random.shuffle(after_top3)

        return res[:3]+after_top3[:num-3]


    def get_skill2(self,jobname="java",num=6):
        """
        直接从技能词库中抽取出来,取最高频率前３个，加后面随机num-3个.
        """
        key_words = self.skill_db[jobname]

        res = [ w for w in key_words[:int(num*np.log(num))]]

        for word in jieba.cut(jobname):
            word = strQ2B(word).lower()
            if word in self.skill_words and word not in res:
                res.insert(0,word)

        after_top3 = res[3:]
        np.random.shuffle(after_top3)

        key_words = res[:3]+after_top3[:num-3]
        key_words.sort()

        return key_words



    def get_jd_with_kmeans(self,jobname='python',duty_num=4,demand_num=5,skill_num=6):
        jobname = self.get_closet_jobname(jobname)
        duty_num,demand_num,skill_num = map(lambda x:int(strQ2B(str(x).decode('utf-8'))),[duty_num,demand_num,skill_num])
        res = OrderedDict()
        res['duty'] = self.get_duty(jobname,duty_num)
        res['demand'] = self.get_demand(jobname,demand_num)
        res['skill1'] = self.get_skill(jobname,skill_num)
        res['skill2'] = self.get_skill2(jobname,skill_num)
        return res

    
    def get_jd_with_textrank(self,jobname='python',duty_num=4,demand_num=5,skill_num=6):
        jobname = self.get_closet_jobname(jobname)
        res = OrderedDict()
        
        duty_num,demand_num,skill_num = map(lambda x:int(strQ2B(x.decode('utf-8'))),[duty_num,demand_num,skill_num])

        self.tk4sents.train(text='\n'.join(self.clear_jd(self.jd_database[jobname]['duty'])))
        duty = self.tk4sents.get_key_sentences(duty_num)
        res['duty'] = sorted(duty,cmp = lambda x,y:self.duty_score(x)-self.duty_score(y))

        self.tk4sents.train(text='\n'.join(self.clear_jd(self.jd_database[jobname]['demand'])))
        demand = self.tk4sents.get_key_sentences(demand_num)
        res['demand'] = sorted(demand,cmp = lambda x,y: self.demand_score(x)-self.demand_score(y))

        self.tk4words.train('\n'.join(self.clear_jd(self.jd_database[jobname]['demand'])))
        res['skill'] = self.tk4words.get_keywords(skill_num,word_min_len=1)
 #       res['skill_phrases'] = self.tk4words.get_keyphrases(skill_num*2,min_occur_num=2)
        return res


from optparse import OptionParser
if __name__ == "__main__":
    parser = OptionParser()
    jobname = sys.argv[1]
    duty_num = sys.argv[2]
    demand_num = sys.argv[3]
    skill_num = sys.argv[4]

    test = AutoGenJD()
    res = test.get_jd_with_kmeans(jobname,duty_num,demand_num,skill_num)
    res2 = test.get_jd_with_textrank(jobname,duty_num,demand_num,skill_num)
    for k,v in res.iteritems():
        print k
        for i,line in enumerate(v,1):
             print i,line
        print ''
    for k,v in res2.iteritems():
        print k
        for i,line in enumerate(v,1):
             print i,line
        print ''
