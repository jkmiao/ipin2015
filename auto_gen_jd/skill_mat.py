#!/usr/bin/env python
# coding=utf-8

import codecs,sys,os,re
import simplejson as json
import jieba
from util import strQ2B
from util import leven_distance
import numpy as np
from sklearn.cluster import KMeans
from gensim import models


jieba.load_userdict('./data/skills.txt')



class Skill_Mat(object):
    def __init__(self):
        self.skills_words = [ line.strip() for line in codecs.open('./data/skills.txt','rb','utf-8')]
        self.jd_database = json.load(open('./data/jd_database.json'))
        self.jd_skills_db = json.load(open('./data/jd_skills_db.json'))
    #    self.w2v = models.Word2Vec.load('./data/jdw2v_50.bin')
    #    self.jd_cluster = json.load(open('./data/jobname_cluster_2000.json'))

    
    def train(self,fname="./data/jd_skills_db.json"):
        res = {}
        for jobname in self.jd_database:
            res[jobname] = {}
            tmp = {}
            for line in self.jd_database[jobname]['demand']:
                for word in jieba.cut(line):
                    word = strQ2B(word).lower()
                    if word in self.skills_words:
                        tmp[word] = tmp.get(word,0)+1
            sorted_keywords = sorted(tmp.iteritems(),key=lambda x:x[1],reverse=True)
            res[jobname] =[ w[0] for w in sorted_keywords[:100] if len(w[0])>1]
            if len(jobname)>8 or len(jobname)<3:
                print jobname

        print len(res)
        json.dump(res,open(fname,'wb'),ensure_ascii=False)

    def train2(self):
        res = {}
        i = 0
        for label in self.jd_cluster:
            i += 1
            tmp = {}
            add_jobname = []

            for jobname in self.jd_cluster[label]:
                if jobname in self.jd_database:
                    add_jobname.append(jobname)
               
                    for line in self.jd_database[jobname]['demand']:
                        for word in jieba.cut(line):
                            word = strQ2B(word)
                            if word not in self.skills_words:continue
                            if word not in tmp:
                                tmp[word] = 1
                            else:
                                tmp[word] += 1

            tmp = sorted(tmp.iteritems(),key=lambda x:x[1],reverse=True)
            
            for tmp_jobname in add_jobname:
                if tmp_jobname not in res:
                    res[tmp_jobname] = [w[0] for w in tmp[:100]]
                else:
                    res[tmp_jobname] += [w[0] for w in tmp[:100]]
                
                for word in jieba.cut(tmp_jobname):
                    word = strQ2B(word).lower()
                    if word in self.skills_words and word not in res[tmp_jobname]:
                        res[tmp_jobname].insert(0,word)

            if i%200==0:
                print i

        print 'origin',len(self.jd_database.keys())
        print i,'done'
        print 'len(res)',len(res)
        json.dump(res,open('./data/jd_skills_db.json','wb'))


    def get_top_jobname(self,jobname):
        jobname = strQ2B(jobname).lower()
        if jobname in self.jd_skills_db:
            return jobname

        dis = [ (leven_distance(k,jobname),k) for k in self.jd_skills_db]
        dis.sort()
        return dis[0][1]


    def test(self,jobname):
        res = [] 
        for i,jd_skill in enumerate(self.jd_skills_db[jobname]):
            print i,jd_skill
            if i>100:break
            res.append(jd_skill)
        return res

    def load_data(self,jobnames):
        res = []
        for jobname in jobnames:
            vec = np.zeros(50)
            for word in jieba.cut(jobname):
                if word in self.w2v.vocab:
                    vec += self.w2v[word]
            res.append(vec.tolist())

        print 'job data',len(res)
        print res[0]
        print res[1]

        return res
            

    def kcluster(self,jobnames,k=2000):
        km = KMeans(n_clusters=k,init='k-means++',n_init=200,max_iter=500,verbose=False) 
        data = self.load_data(jobnames)
        km.fit(data)
        labels = map(str,km.labels_)
    #    centers = km.cluster_centers_
    
        label_dict = {}
        for label,name in zip(labels,jobnames):
            if label not in label_dict:
                label_dict[label] = [name]
            else:
                label_dict[label].append(name)

        json.dump(label_dict,open('./data/jobname_cluster_2000.json','wb'))
        return label_dict
  
    def output_skill_mat(self):
        fw = open('./data/jobnames_clusters_2000.txt','wb')
        jds = json.load(open('./data/jobname_cluster_2000.json'))
        for i,jobname in enumerate(jds):
            fw.write("%d\n"%(i+1))
            fw.write("%-20s\t"%jobname.decode('utf-8'))
            fw.write(" , ".join(jds[jobname]))
        fw.close()

    
    def clear_jd_skill(self):
        for jobname in self.jd_skills_db:
            self.jd_skills_db[jobname] = filter(foo,self.jd_skills_db[jobname])
            for word in jieba.cut(jobname):
                if word in self.skills_words and word not in self.jd_skills_db[jobname]:
                    self.jd_skills_db[jobname].insert(0,word)

        json.dump(self.jd_skills_db,open('./data/jd_skills_db2.json','wb'))

def foo(line):
    if re.search(u"工程师|java软件",line):
        return False
    return True


if __name__=="__main__":
    test = Skill_Mat()
    test.train()
