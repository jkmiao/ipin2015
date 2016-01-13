#!/usr/bin/env python
# coding=utf-8

import simplejson as json
import re,sys,codecs
from simhash import Simhash
from util import Mycluster
from collections import OrderedDict
from gensim import models
import jieba
reload(sys)
sys.setdefaultencoding('utf-8')

jieba.load_userdict('./data/skills.txt')

class AutoGenJD(object):
    """
    自动生成ＪＤ职责、要求和技能
    """

    def __init__(self):
        self.CLEAR_NUM = re.compile(u"^\d+[\.,、，：:]|^[\(（【]\d+[\)）\.】]?|^\d\s*[\)）】]")
        self.CLEAR_COLO = re.compile(u"^[，。、\.]（）【】]|[\.，。；：。]$|[\s\xa0]")
        self.jd_database = json.load(open("./data/jd_database.json"))
        self.km = Mycluster()
        self.SKILL = re.compile(u"精通|熟悉|熟练|了解|掌握|善于|懂得|善于|擅长|能力|具有|具备|资格")
        self.NOTSKILL = re.compile(u"岁|学历|专业|年龄|性别|热情|梦想|公司|具有以下条件|优先|者|为人|应届生|积极|主动|生活|保证|一下条件|地址")
        self.skill_db = [token.strip() for token in codecs.open('./data/skills.txt','rb','utf-8')]
        self.w2v = models.Word2Vec.load('./data/word2vec.model')

    def is_most_english(self,line):
        en_word = [ c for c in line if (c>=u'\u0041' and c<=u'\u005a') or (c>=u'\u0061' and c<=u'\u007a') ]
        return float(len(en_word))/len(line)>0.7


    def clear_jd(self,linelist):
        """
        清洗数据，去除句子前后的序号、数字、标点符号等
        """
        res = set()
        for line in linelist:
            line = line.strip()
            if re.search(u"[；;\.。，、：:]\d+",line) or len(line)<8 or len(line)>35:continue
            if self.is_most_english(line):continue
            line = self.CLEAR_NUM.sub("",line)
            line = self.CLEAR_COLO.sub("",line)
            res.add(line)
        return res


    def get_closet_jobname(self,jobname='java'):
        dis = [ (Simhash(jobname).distance(Simhash(other)),other) for other in self.jd_database.keys() ]
        sorted_jobname = sorted(dis,key = lambda x:x[0])
        for k,v in sorted_jobname[:5]:
            print k,v
        return sorted_jobname[0][1]



    def get_demand(self,jobname='python',num=6):
        """
        使用kmeans 聚类，相同一类只出现一句，排序后输出
        """
        def demand_score(line):
            s = len(line)+100
            if re.search(u"男|女|性别|岁|不限",line):
                s -= 60
            if re.search(u"学历|专业|\d+[kK元]",line):
                s -= 40
            if re.search(u"经验",line):
                s -= 20
            return s
                    
        jd_demand = self.clear_jd(self.jd_database[jobname]['demand'])
        if len(jd_demand)<int(num):
            res = jd_demand
        else:
            res = self.km.kcluster(jd_demand,k=int(num))
        return sorted(res,cmp = lambda x,y:demand_score(x)-demand_score(y))


    def get_duty(self,jobname="python",num=4):
        """
        同理句子聚类后输出，每一类输出一句
        """
        def duty_score(line):
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
        
        jd_duty = self.clear_jd(self.jd_database[jobname]['duty'])
        if len(jd_duty)<int(num):
            res = jd_duty
        else:
            res = self.km.kcluster(jd_duty,k=int(num))
        return sorted(res,cmp = lambda x,y:duty_score(x)-duty_score(y))

    def get_skill(self,jobname="python",num=5):
        """
        从demand中关键词抽出相关技能短语
        """
        key_words = {}
        
        jd_skill = self.clear_jd('\n'.join(self.jd_database[jobname]['demand']).split())
        jd_skill = filter(lambda line:self.SKILL.search(line),jd_skill)
        for line in jd_skill:
            for word in jieba.cut(line):
                if word.lower() in self.skill_db:
                    key_words[word.lower()] = key_words.get(word.lower(),0)+1

        sorted_skill_words = sorted(key_words,key=lambda x:x[1],reverse=True)

        res = [ w[0] for w in sorted_skill_words[:num] ]

#        jd_skill = filter(lambda line: not self.NOTSKILL.search(line),jd_skill)
#        if len(jd_skill)<int(num):
#            res = jd_skill
#        else:
#            res = self.km.kcluster(jd_skill,k=int(num))
#        key_words = list(key_words)
#        res = sorted(res)
#        return res,key_words
        return res


    def get_jd_with_kmeans(self,jobname='python',duty_num=4,demand_num=5,skill_num=6):
        jobname = self.get_closet_jobname(jobname)
        res = OrderedDict()
        res['duty'] = self.get_duty(jobname,duty_num)
        res['demand'] = self.get_demand(jobname,demand_num)
        res['skill'],res['skill_key_words'] = self.get_skill(jobname,skill_num)
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
    for k,v in res.iteritems():
        print k
        for i,line in enumerate(v,1):
             print i,line
        print ''
