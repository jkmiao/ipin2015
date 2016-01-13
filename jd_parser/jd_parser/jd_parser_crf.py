#!/usr/bin/env python
# coding=utf-8

import codecs,sys
import re
from util import strQ2B
import pycrfsuite 
from collections import Counter
from tgrocery import Grocery

reload(sys)
sys.setdefaultencoding('utf-8')



class JdCRF(object):
    def __init__(self):
        self.data = []
        self.clf = Grocery("jdclf")
        self.clf.load()
        
        self.SEX = re.compile(u"性别不限|性别|男|女")
        self.AGE = re.compile(u"\d+周?岁|年龄")
        self.DEGREE = re.compile(u"(全日制)?(初中|高中|中专|大专|专科|大学专科|中职|本科|大学本科|硕士|研究生|博士|博士后)(.?以上)?")
        self.MAJOR = re.compile(u"\S+(相关专业|专业优先|及其.专业|[类等]专业[优先]?)")
        self.EXP = re.compile(u"工作经验：|工作经[历验]|工作年限|年.{0,4}经[历验]|经[历验].{1,6}年")
        self.PUB_TIME = re.compile(u"(\d+)(天前发布)")
        
        self.INCNAME = re.compile(u"\S+(有限公司|酒店|银行|集团|研究中心|研究所|学校|旅行社|分?公司|研发中心|技术部|事.部|招聘)") 
        self.NOT_INC = re.compile(u"职位|描述|收藏|推荐|地址|邮箱|主页|介绍|欢迎|加入|要求|简介|险一金|奖金|包吃住|社区|厂房|人员|职责") 
        self.INCTAG = re.compile(u"大公司|五百强|全球500强|小公司|成长型公司|创业公司|私有经济|集体经济|集团|外企|已上市|稳定性高|平均年龄\d岁|妹纸多|学历高|福利待遇好|晋升机会大|民营公司|民营企业\
                                 |互联网|创业型|国企|央企")

        self.JOBNAME = re.compile(u'\S*(研发工程师|工程师|经理|助理|顾问|前台|秘书|主管|研究员|实习生|操作员|专员|教学人员|技术人员|管理员|业务员|公关|程序员|教师|老师|培训生|\
                                  文员|研究员|策划|主任|总监|设计师|分析师|架构师|摄影师|编辑|BD|游戏UI|Android(开发)?|PHP(开发)?|Python(开发)?|.?(急招|急聘|初级|中级|高级|方向).?[\s）】\)])|\
                                  |行政人事|网店设计|客服|会计|电话销售|外贸跟单|web前端|游戏UI|后.开发|产品运营|商业数据分析')

        self.START_DEMAND = re.compile(u"(岗位要求|应聘条件|任职要求|岗位资格|任职资格|岗位条件|工作要求|任职条件|人员条件|职位.求|职位条件|职位描述|岗位资格|职位资格|具备条件)[:：\s]\
                                       |如果你.{0,10}[:：\s]|我们希望你.{0,12}[:：\s]|(要求|条件)[:：\s]|你需要?具备什么.+[？\?:：\s]|任职资格[:：\s]")

        self.DEMAND = re.compile(u"熟悉|熟练|具有|善于|懂得|掌握|具备|能够|优先|不少于|不超过|至少|团队.作|良好的|工作经验|开发经验|实习经历|能力强|富有|以上学历|经验|喜欢|\
                                 较强的.{2,8}能力|相关专业|相关学历|者优先|精通|了解|及以上|技术全面|.强的责任心|[能有]独立|英文流利")

        self.DUTY = re.compile(u"跟进|协助|负责|配合|其他工作|领导交办的|对.+提供|审核|参与|提出|跟踪|报告|为.+提出|日常.+工作|指导|跟进|拓展|运营|用户|客户|协调|拟写|通过|协同\
                               |完成|沟通|需求|秘书.{2,5}翻译")

        self.START_DUTY = re.compile(u"(岗位职责|岗位描述|职位描述|职责描述|任职描述|职位职责|工作职责|工作职能|职位职能|工作内容|实习内容|职位内容)[:：\s]|做这样的事[:：\s]|职责.{0,5}[:：\s]")

        self.PAY = re.compile(u"薪酬|待遇|月薪|薪资|年薪|底薪|\d+k|\d+万|\d+元|工资|报酬|薪水|福利")

        self.BENEFIT = re.compile(u"周休|补助|补贴|假日|餐补|提成|交通补助|食宿|加班工资|期权|年假|领导|扁平化|管理|氛围|空间|休假|月假|带薪|全休|晋升|培训|舒适的|旅游|奖励|过节费|五险一金|奖金|\
                                  |弹性工作|氛围|成长空间|实训|培训|高薪|前景|旅游|活动|分红")
        
    


    def gen_data(self,fname='./data/lagou_train.txt'):
        fw = codecs.open('./data/jd_train_crf.txt','wb','utf-8')
        cnt = 1
        for line in codecs.open(fname,'rb','utf-8'):
            if line.startswith(u"====="):
                fw.write(line)
                continue

            cnt +=1
            if len(line.strip())>1:
                    pred = self.clf.predict(line)
                    newline = pred+'\t\t'+line.strip()+'\t\t'+str(len(line))+"\n"
                    fw.write(newline)
        print cnt
        print 'done'


    def load_data(self,fname="./data/jd_train_crf.txt"):
        data = []
        tmp = []
        for line in codecs.open(fname,'rb','utf-8'):
            if line.startswith(u"===="):
                data.append(tmp)
                tmp = []
                continue
            else:
                tag_data = line.strip().split('\t\t')
                if len(tag_data)==3:
                    tmp.append(tuple(tag_data))
                else:
                    print '\t  '.join(tag_data)

        
        n = len(data)/2
        print 'train data',n
        print 'test data',len(data)-n
        return data[n:],data[:n]
    

    def word2features(self,sent,i):
        word = sent[i][0]
        postag = sent[i][1]

        features = [
            'bias',
            'word.lower=' + word.lower(),
            'word[:2]=' +word[:2],
            'word.isdigit=%s'%word.isdigit(),
            'postag='+postag,
            'demand=%s'% '1' if self.DEMAND.search(word) else '0',
            'start_demand=%s'% '1' if self.START_DEMAND.search(word) else '0',
            'start_duty=%s'% '1' if self.START_DUTY.search(word) else '0',
            'duty=%s'% '1' if self.DUTY.search(word) else '0',
            'jobname=%s'% '1' if self.JOBNAME.search(word) else '0',
            'incname=%s'% '1' if self.INCNAME.search(word) else '0',
            'benefit = %s'% '1' if self.BENEFIT.search(word) else '0',
            'pred=%s' % self.clf.predict(word)
        ]

        if i>0:
            word1 = sent[i-1][0]
            postag1 = sent[i-1][1]

            features.extend([
                '-1:postag='+postag1,
                '-1:word.islower='+word1[:3].lower(),
                '-1:start_demand=%s'% '1' if self.START_DEMAND.search(word) else '1',
                '-1:start_duty=%s'% '1' if self.START_DUTY.search(word) else '0',
                '-1:demand=%s'% '1' if self.DEMAND.search(word1) else '0',
                '-1:duty=%s'% '1' if self.DUTY.search(word1) else '0',
                '-1:jobname=%s'% '1' if self.JOBNAME.search(word1) else '0',
                '-1:incname=%s'% '1' if self.INCNAME.search(word1) else '0',
                '-1:benefit = %s'% '1' if self.BENEFIT.search(word) else '0',
                '-1:pred=%s' % self.clf.predict(word),
            ])

        else:
            features.append('BOS')


        if i<len(sent)-1:
            word1 = sent[i+1][1]
            postag1 = sent[i+1][1]
            features.extend([
                '+1:word.lower=' + word1[:3].lower(),
                '+1:word.istitle=%s' % word1.istitle(),
                '+1:word.isupper=%s' % word1.isupper(),
                '+1:postag=' + postag1,
                '+1:postag[:2]=' + postag1[:2],
                '+1:start_demand=%s'% '1' if self.START_DEMAND.search(word) else '0',
                '+1:start_duty=%s'% '1' if self.START_DUTY.search(word) else '0',
                '+1:demand=%s'% '1' if self.DEMAND.search(word1) else '0',
                '+1:duty=%s'% '1' if self.DUTY.search(word1) else '0',
                '+1:jobname=%s'% '1' if self.JOBNAME.search(word1) else '0',
                '+1:incname=%s'% '1' if self.INCNAME.search(word1) else '0',
                '+1:benefit = %s'% '1' if self.BENEFIT.search(word) else '0',
                '+1:pred=%s' % self.clf.predict(word),
            ])
        else:
            features.append('EOS')


        return features




    def sent2features(self,sent):
        return [self.word2features(sent,i) for i in range(len(sent))]

    def sent2labels(self,sent):
        return [label for (label,token,postag) in sent]

    def sent2tokens(self,sent):
        return [token for (label,token,postag) in sent]
    

    def train(self,x_train,y_train):
        
        assert len(x_train)==len(y_train),"not the same %d  %d"%(len(x_train),len(y_train))

        trainer = pycrfsuite.Trainer(verbose=False)

        for xseq,yseq in zip(x_train,y_train):
            trainer.append(xseq,yseq)

        trainer.set_params({
            'c1':1.0,
            'c2':1e-3,
            'max_iterations':50,
            'feature.possible_transitions':True
        })

        trainer.train('jd_skill.crfsuite')

    
    def test(self,sent):
        tagger = pycrfsuite.Tagger()
        tagger.open('./jd_skill.crfsuite')
        
        print 'tokens   ','\n '.join(self.sent2tokens(sent))
        print 'Predicted','\t '.join(tagger.tag(self.sent2features(sent)))
        print 'Correct  ','\t '.join(self.sent2labels(sent))




if __name__=="__main__":
    model = JdCRF()
#    model.gen_data()
    train_sents,test_sents = model.load_data()
    x_train = [model.sent2features(s) for s in train_sents]
    y_train = [model.sent2labels(s) for s in train_sents] 

    # x_test = [ model.sent2features(s) for s in test_sents]
    y_test = [ model.sent2labels(s) for s in test_sents ]


    model.train(x_train,y_train)
    print 'y_test' ,y_test[0]
    model.test(test_sents[0])


