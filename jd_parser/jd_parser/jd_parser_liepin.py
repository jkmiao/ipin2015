#!/usr/bin/env python
# coding=utf-8

import sys,re,codecs,jieba
from bs4 import BeautifulSoup
from urllib2 import urlopen
from collections import OrderedDict,Counter
from base import JdParserTop

reload(sys)
sys.setdefaultencoding('utf-8')


class JdParserLiePin(JdParserTop):
    """
    对lagou Jd 结合html 进行解析
    """
    def __init__(self):
        JdParserTop.__init__(self)
        self.result = OrderedDict()


    def preprocess(self,htmlContent,fname=None,url=None):
        self.result.clear()
        html = ""
        if url!=None:
            html = urlopen(url).read()
        elif htmlContent:
            html = htmlContent
        elif fname:
            html = open(fname).read()
        
        if len(html)<60 or re.search(u"猎头等级|服务好评率",html):
            raise Exception("input arguments error")
        
        self.html= re.sub(u"<br.?/?>|<BR.?/?>|<br>",u"\n",html)

        self.soup = BeautifulSoup(self.html)

        self.jdsoup = self.soup.find("div","title")
        self.compsoup =self.soup.find("div","side").find("div","right-post-top")

        self.jdstr = self.jdsoup.find("div","content content-word").get_text().strip()
        self.linelist = [ line.strip() for line in self.SPLIT_LINE.split(self.jdstr) if len(line)>1]
    
        # 针对基本信息，提前存储，方便解析基本字段
        self.jdtop_soup = self.jdsoup.find("div","job-main").find("div","job-title-left")
        self.jdtop2_soup = self.jdsoup.find("div","job-main").find("div","job-title-left").find("div","resume clearfix").find_all("span")
        self.jdbasic_soup = self.jdsoup.find("div","job-main main-message ").find("div","content")
        self.jdbasic_soup = self.jdbasic_soup.find_all("li")
   



    def regular_incname(self):
        inc_name = self.compsoup.find('p',"post-top-p").get_text()
        self.result['incName'] = inc_name.strip()


    def regular_inc_tag(self):
        res = {"incIntro":"None","incUrl":"None"}
        inc_tags = [line.strip() for line in self.compsoup.find("div","content content-word").get_text().split() if len(line)>1 ]
        

        for tag in inc_tags:
            kv = re.split(u"[:：]",tag)
            if len(kv)>1:
                key,value = kv[0],kv[1]
                if re.search(u"规模",key):
                    res["incScale"] = value.strip()
                elif re.search(u"性质",key):
                    res["incType"] = value.strip()
                elif re.search(u"地址",key):
                    res["incLocation"] = value.strip()
                elif re.search(u"网站",key):
                    res["incUrl"] = value.strip()

        res["incIndustry"] = self.compsoup.find("div","content content-word").find("a").get_text().strip()
        find_inc_intro = self.soup.find("div",{"class":"job-main main-message noborder ","data-selector":"introduction"})

        if re.search(u"企业介绍",self.html) and find_inc_intro: 
            res["incIntro"] = find_inc_intro.get_text().strip()
            incUrl = re.search(u"(公司网站|官网)[:\s： ]([\w\d\./_:]+.com)",res["incIntro"])
            if not res["incUrl"] and incUrl:
                res["incUrl"] = re.search("[\w\d\./_:]+",incUrl.group()).group() 

        self.result.update(res)



    def regular_pubtime(self):
        """
        发布时间 & 截止时间
        """
        pub_time = self.jdtop_soup.find("p","basic-infor").find_all("span")[1].get_text()
        self.result["pub_time"] = re.sub(u"[:：　\s\n]|发布于","",pub_time)



    def regular_jobname(self):
        jobname = self.jdsoup.find("div","title-info").find('h1').get_text()
        self.result['jobName'] = self.CLEAN_JOBNAME.sub("",jobname)


    def regular_job_tag(self):
        res = {"jobCate":"",'jobType':"全职","jobNum":""}
        if re.search(u"实习",self.result["jobName"]):
            res["jobType"]=u"实习"
        
        self.result.update(res)

    def regular_sex(self):
        """
        不限:0
        男:1
        女:2
        """
        res = u"不限"
        for line in self.jdbasic_soup:
            key,value = re.split(u"[:：]",line.get_text())
            if re.search(u"性别",key):
                if re.search(u"性别不限|男女不限|不限",value):
                    res = u"不限"
                elif re.search(u"男",value):
                    res = u"男"
                elif re.search(u"女",value):
                    res = u"女"
                break

        self.result['sex'] = str(res)


    def regular_age(self):
        """
        [minage,maxage]
        """ 
        res = [0,100]
        agestr = self.jdtop2_soup[-1].get_text()

        age = re.findall(u"\d+",agestr)
        if len(age)>1:
            res = (age[0],age[-1])
        elif len(age)==1:
            if re.search(u"以上|不低于|至少|大于|超过",agestr):
                res[0] = age[0]
            elif re.search(u"小于|低于|不超过|不得?高于|以下|不大于",agestr):
                res[1] = age[0]
            else:
                res[0] = int(age[0])-3
                res[1] = int(age[0])+3

        self.result['age'] = map(str,res)


    def regular_major(self):
        res = []
        for line in self.jdbasic_soup:
            key,value = re.split(u"[:：]",line.get_text())
            if re.search(u"专业要求",key):
                if re.search(u"不限",value):
                    res = []
                    break
                else:
                    for token in jieba.cut(value):
                        if token in self.majordic:
                            res.append(token)

        self.result["major"] = res



    def regular_degree(self):
        degree = self.jdtop2_soup[0].get_text().strip()
        for w in jieba.cut(degree):
            if w in self.degreedic:
                degree = w
                break
        self.result['degree'] = degree



    def regular_exp(self):
        res = [0,100]
        expstr = self.jdtop2_soup[1].get_text()
        
        exp = re.findall("\d+",expstr)
        if len(exp)==1:
            if re.search(u"以上|大于|至少",expstr):
                res[0]= exp[0]

        self.result['exp'] = map(str,res)
    

    def regular_skill(self):
        res = []
        #　先加上语言要求
        res.append(self.jdtop2_soup[2].get_text().strip())
        for line in self.linelist:
            for word in jieba.cut(line):
                word = word.lower()
                if word in self.skilldic:
                    res.append(word)
        res =[w[0] for w in Counter(res).most_common(4)]
        self.result["skill"] = res



    def regular_workplace(self):
        res = self.jdtop_soup.find("p","basic-infor").find("span").get_text().strip()        
        self.result['workplace'] = res



    def regular_pay(self):
        res = [0,0]
        paystr = self.jdtop_soup.find("p","job-main-title").get_text()
        if re.search(u"万",paystr):
            pay = re.findall("\d+",paystr)
            if len(pay)==1:
                res[0] = int(pay[0]+"0000")/12
            elif len(pay)>1:
                res[0],res[1] = int(pay[0]+"0000")/12,int(pay[1]+"0000")/12
        self.result['pay'] = map(str,res)

    
    def regular_cert(self):
        res = []
        linelist = [line for line in re.split(u"[\s，。；、]",self.jdstr) if 3<len(line)<10 ]
        for line in linelist:
            findcert = re.search(u"(\S+证书|CET-\d|普通话|英语|口语|.语|日文|雅思|托福|托业)(至少)?(通过)?[\d一二三四五六七八九]级[及或]?(以上)?|(英语)?CET-\d级?(以上)?|职业资格|律师证|会计证",line)
            if findcert:
                res.append(findcert.group())
            else:
                findcert = re.search(u"有(.+证)书?",line)
                if findcert:
                    res.append(findcert.group(1))
                else:
                    findcert = re.search(u"有.+资格",line)
                    if findcert:
                        res.append(findcert.group())
        self.result['cert'] = re.sub(u"[或及以上]","",' / '.join(res))
        self.result['cert'] = self.result['cert'].split(' / ')

    


    def regular_demand(self):
        jdstr = self.jdstr
        res,linelist = [],[]
        pos = list(self.START_DEMAND.finditer(jdstr))
        if len(pos)>0:
            linelist = [ re.sub("[\s　]+"," ",line) for line in self.SPLIT_LINE.split(jdstr[pos[-1].span()[1]:]) if line>3]
        
        linelist = filter(lambda x:len(x)>2,linelist)
        for i in range(len(linelist)):
            line = linelist[i]
            if self.START_DEMAND.search(line):
                continue
            if self.START_DUTY.search(line) or self.DUTY.search(line):
                break
            if re.match(u"\d[、.\s ]|[（\(【][a-z\d][\.、\s ]|[\u25cf\uff0d]",line) or self.DEMAND.search(line) or self.clf.predict(line)=="demand":
                res.append(self.CLEAN_LINE.sub("",line))
            elif i<len(linelist)-1 and self.clf.predict(linelist[i+1])=='demand':
                res.append(self.CLEAN_LINE.sub("",line))
            else:
                break

        if not res:
            linelist = [ self.clean_line(line) for line in self.SPLIT_LINE.split(jdstr) if len(line.strip())>5]
            for line in linelist:
                if self.clf.predict(line)=='demand':
                    res.append(self.CLEAN_LINE.sub("",line))
        
        res = [str(i+1)+'. '+line for i,line in enumerate(res)]
        self.result['demand'] = '\n'.join(res)

    def regular_duty(self):

        jdstr = self.jdstr
        res,linelist = [],[]
        pos = list(self.START_DUTY.finditer(jdstr))
        if len(pos)>0:
            linelist = [ re.sub("[\s　]+"," ",line) for line in self.SPLIT_LINE.split(jdstr[pos[-1].span()[1]:]) if line>3]
        
        linelist = filter(lambda x:len(x)>2,linelist)
        for i in range(len(linelist)):
            line = linelist[i]
            if self.START_DUTY.search(line):
                continue
            if self.START_DEMAND.search(line) or self.DEMAND.search(line):
                break
            if re.match(u"\d[、.\s ]|[（\(【][a-z\d][\.、\s ]|[\u25cf\uff0d]",line) or self.DUTY.search(line) or self.clf.predict(line)=="duty":
                res.append(self.CLEAN_LINE.sub("",line))
            elif i<len(linelist)-1 and self.clf.predict(linelist[i+1])=='duty':
                res.append(self.CLEAN_LINE.sub("",line))
            else:
                break
        if not res:
            linelist = [ self.clean_line(line) for line in self.SPLIT_LINE.split(jdstr) if len(line.strip())>5]
            for line in linelist:
                if self.clf.predict(line)=='duty':
                    res.append(self.CLEAN_LINE.sub("",line))
        
        res = [str(i+1)+'. '+line for i,line in enumerate(res)]

        self.result['duty'] = '\n'.join(res)



    def regular_benefit(self):
        jdstr = self.jdsoup.find("div","").get_text()
        res,linelist = [],[]
        
        job_tags = self.jdsoup.find("div","job-main").find("div","tag-list clearfix")
        if job_tags:
            job_tags = job_tags.find_all("span","tag")
            for tag in job_tags:
                res.append(tag.get_text())

        pos = list(self.START_BENEFIT.finditer(jdstr))
        if not res and len(pos)>0:
            linelist = [ re.sub("[\s　]+"," ",line) for line in self.SPLIT_LINE.split(jdstr[pos[-1].span()[1]:]) if line>3]
            for i in range(len(linelist)):
                line = linelist[i]
                if len(line)<2:
                    continue
                if re.match(u"\d[、.\s ]|[（\(【][a-z\d][\.、\s ]|[\u25cf\uff0d]",line) or self.clf.predict(line)=="benefit":
                    res.append(line)
                elif i<len(linelist)-1 and self.clf.predict(linelist[i+1])=='benefit':
                    res.append(line)
                else:
                    break
        
                res = [str(i+1)+'. '+line for i,line in enumerate(res)]

        self.result['benefit'] = '\n'.join(res)


    def parser(self,htmlContent=None,fname=None,url=None):
        self.preprocess(htmlContent,fname,url)
        self.regular_incname()
        self.regular_inc_tag()
        self.regular_pubtime()
        self.regular_jobname()
        self.regular_job_tag()
        self.regular_sex()
        self.regular_age()
        self.regular_major()
        self.regular_degree()
        self.regular_exp()
        self.regular_skill()
        self.regular_workplace()
        self.regular_pay()
        self.regular_cert()
        self.regular_demand()
        self.regular_duty()
        self.regular_benefit()

        return self.result

    def ouput(self):
        for line in self.linelist:
            print line

        for k,v in self.result.iteritems():
            print k
            if isinstance(v,list):
                print "[",",".join(v),"]"
            else:
                print v

import os
if __name__ == "__main__":
    test = JdParserLiePin()
    path = './test_jds/liepin/'
    fnames = [ path+fname for fname in os.listdir(path) ]
    for fname in fnames[-10:]:
        try:
            print '==='*20,fname
            htmlContent = codecs.open(fname,'rb','utf-8').read()
            test.parser(htmlContent,fname=None,url=None)
            test.ouput()
        except Exception,e:
            print 'e',e
            continue


