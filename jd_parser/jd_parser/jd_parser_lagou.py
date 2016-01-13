#!/usr/bin/env python
# coding=utf-8

import sys,re,codecs,jieba
from bs4 import BeautifulSoup
from urllib2 import urlopen
from util import strQ2B
from collections import OrderedDict,Counter
from base import JdParserTop
from threading import Thread

reload(sys)
sys.setdefaultencoding('utf-8')


class JdParserLagou(JdParserTop):
    """
    对lagou Jd 结合html 进行解析
    """
    def __init__(self):
        JdParserTop.__init__(self)
        self.result = OrderedDict()
        


    def preprocess(self,htmlContent=None,fname=None,url=None):
        self.result.clear()
        html = ""
        if url!=None:
            html = urlopen(url).read()
        elif htmlContent:
            html = htmlContent
        elif fname:
            html = codecs.open(fname,'rb','utf-8').read()
        
        if len(html)<60:
            raise Exception("error input")
        
        self.html= re.sub(u"<br./?./?>|<BR.?/?>|<br>",u"。",html)
        soup = BeautifulSoup(self.html)

        self.jdsoup = soup.find("dl","job_detail")
        self.compsoup = soup.find("dl","job_company")
        self.jdstr = self.jdsoup.find("dd","job_bt").get_text()

        self.linelist = [ line.strip() for line in self.SPLIT_LINE.split(self.jdstr) if len(line)>2]
    
    
    def regular_inc_name(self):
        link = self.compsoup.find("dt").find("img",{"class":"b2"})
        res = ""
        if ('alt' in dict(link.attrs)):
            incname1 = link['alt']
            res = incname1
        else:
            res = self.compsoup.find("dt").find("h2","fl").get_text().split()[0]
        self.result["incName"] = res



    def regular_inc_tag(self):
        """
        行业，类型，规模、介绍、公司主页url、目前阶段、公司地址
        """
        res = {}
        
        inc_tags = self.compsoup.find_all("ul")
        for ul_tag in inc_tags:
            li_tags = ul_tag.find_all("li")
            for tag in li_tags:
                key,val = tag.span.get_text(),tag.text.split()[-1]
                if re.search(u"领域",key):
                    res["incIndustry"]=val.strip()
                elif re.search(u"规模",key):
                    res["incScale"] = val.strip()
                elif re.search(u"主页",key):
                    res["incUrl"]= val.strip()
                elif re.search(u"目前阶段",key):
                    res["incIntro"]= val.strip()
        inc_place = self.compsoup.find("div",{"id":"smallmap"}).findPrevious("div").get_text()
        res["incLocation"] = inc_place.strip()
        res["incType"] = u"IT"
        self.result.update(res)


    def regular_pubtime(self):
        """
        发布时间 & 截止时间
        """
        pub_time = self.jdsoup.find("p","publish_time").get_text().split()[0]
        self.result["pub_time"] = pub_time
        self.result["end_time"] = ""



    def regular_jobname(self):
        jobname = self.jdsoup.find("dt","clearfix join_tc_icon").find('h1').get_text().split()[-1]
        self.result['jobName'] = self.clean_jobname(jobname.strip())


    def regular_jobtag(self):
        """
        返回职位性质，职位类别，招聘人数
        """
        res = {"jobType":"全职","jobCate":"","jobNum":""}

        res["jobType"] = self.jdsoup.find("dd","job_request").find_all("span")[-1].get_text()
        res["jobCate"] = self.result["incIndustry"]
        if re.search(u"实习|兼职",self.result["jobName"]):
            res["jobType"]=u"实习"
        self.result.update(res)


    def regular_sex(self):
        """
        不限:0
        男:1
        女:2
        """
        res = u"不限"
        for line in self.linelist:
            if self.SEX.search(line):
                if re.search(u"性别不限|男女不限",line):
                    res = u"不限"
                elif re.search(u"男",line):
                    res = u"男"
                elif re.search(u"女",line):
                    res = u"女"
                break

        self.result['sex'] = str(res)


    def regular_age(self):
        """
        (minage,maxage)
        """ 
        res = [0,100]
        for line in self.linelist:
            if re.search(u"\d+后",line):continue
            if self.AGE.search(line):
                findage = re.search(u"(\d{2}[\-－到至])?\d{2}岁|(至少|不低于|不超过|不大于|大概|大约|不少于|大于)?\d+周?岁|\d+周岁(以上|左右|上下)",line)
                if findage:
                    agestr = findage.group()
                    age = re.findall(u"\d{,2}",agestr)
                    if len(age)>=2:
                        res = (age[0],age[1])
                    elif len(age)==1:
                        if re.search(u"以上|不低于|至少|大于|超过",line):
                            res[0] = age[0]
                        elif re.search(u"小于|低于|不超过|不得?高于|以下|不大于",line):
                            res[1] = age[0]
                        elif re.search(u"左右|大约|大概",line):
                            res[0],res[1] = int(age[0])-3,int(age[-1])+3
                    break

        self.result['age'] = map(str,res)


    def regular_major(self):
        res = []
        for line in self.linelist:
            for word in jieba.cut(line):
                if word.lower() in self.majordic or word[:-2] in self.majordic:
                    res.append(word)

        self.result["major"] = list(set(res))



    def regular_degree(self):
        degree =  self.jdsoup.find("dd","job_request").find_all("span")[3].get_text().strip()
        for w in jieba.cut(degree):
            if w in self.degreedic:
                degree = w
                break
        self.result['degree'] = degree



    def regular_exp(self):
        res = [0,100]
        expstr =  self.jdsoup.find("dd","job_request").find_all("span")[2].get_text()
        exp = re.findall("\d+",expstr)
        if len(exp)==1:
            res[0] = exp[0]
        elif re.search(u"半",expstr):
            res[0] = 0.5
        elif len(exp)>1:
            res = (exp[0],exp[-1])
        self.result['exp'] = map(str,res)
    

    def regular_skill(self):
        res = []
        for line in self.linelist:
            for word in jieba.cut(line):
                word = word.lower()
                if word in self.skilldic:
                    res.append(word)
        res =[w[0] for w in Counter(res).most_common(5)]
        self.result["skill"] = res



    def regular_workplace(self):
        workplace =  self.jdsoup.find("dd","job_request").find_all("span")[1].get_text().strip()
        self.result['workplace'] = workplace



    def regular_pay(self):
        res =[0,0]
        paystr =  self.jdsoup.find("dd","job_request").find_all("span")[0].get_text().strip()
        if paystr:
            pay = map(lambda x: re.sub("k","000",x),re.findall("\d+[kK]",paystr))
            if len(pay)==2:
                res[0] = pay[0]
                res[1] = pay[-1]

        self.result['pay'] = map(str,res)

    
    def regular_cert(self):
        res = []
        for line in self.linelist:
            findcert = self.CERT.search(line)
            if findcert:
                res.append(findcert.group())
            else:
                findcert = re.search(u"有(.+证)",line)
                if findcert:
                    res.append(findcert.group(1))

        res = re.sub(u"[或及以上]","",'|'.join(res))
        self.result['cert'] = res.split('|')

    

    def regular_demand(self):
        
        res,linelist = [],[]

        pos = list(self.START_DEMAND.finditer(self.jdstr))
        if pos:
            linelist = [re.sub("[\s　]+"," ",line.strip()) for line in self.SPLIT_LINE.split(self.jdstr[pos[-1].span()[1]:]) if len(line)>3]

        linelist = filter(lambda x:len(x)>2,linelist)

        for i in range(len(linelist)):
            line = linelist[i]
            if self.START_DEMAND.search(line):
                continue
            if self.START_DUTY.search(line):
                break
            if re.match(u"\d[、\.\s]|[（\(]?[a-z\d][\.、\s]",line) or self.DEMAND.search(line) or self.DEMAND.search(line) or self.clf.predict(line)=='demand':
                res.append(self.clean_line(line))
            elif i<len(linelist)-1 and self.clf.predict(linelist[i+1])=='demand':
                res.append(self.clean_line(line))
            else:
                break

        if not res:
            for line in self.linelist:
                if self.clf.predict(line)=='demand':
                    res.append(self.clean_line(line))

        res = [str(i+1)+'.'+line for i,line in enumerate(res)]

        self.result['demand'] = '\n'.join(res)


    def regular_duty(self):
        
        res,linelist = [],[]

        pos = list(self.START_DUTY.finditer(self.jdstr))
        if pos:
            linelist = [re.sub("[\s　]+"," ",line.strip()) for line in self.SPLIT_LINE.split(self.jdstr[pos[-1].span()[1]:]) if len(line)>3]
        
        linelist = filter(lambda x:len(x)>2,linelist)

        for i in range(len(linelist)):
            line = linelist[i]
            if self.START_DUTY.search(line):
                continue
            if self.START_DEMAND.search(line):
                break
            if re.match(u"\d[、\.\s]|[（\(]?[a-z\d][\.、\s][\u25cf\ff0d]",line) or self.DUTY.search(line) or self.clf.predict(line)=='duty':
                res.append(self.clean_line(line))
            elif i<len(linelist)-1 and self.clf.predict(linelist[i+1])=='duty':
                res.append(self.clean_line(line))
            else:
                break
        if not res:
            for line in self.linelist:
                if self.clf.predict(line)=='duty':
                    res.append(self.clean_line(line))

        res = [str(i+1)+'. '+line for i,line in enumerate(res)]

        self.result['duty'] = '\n'.join(res)


    def regular_benefit(self):
        
        res,linelist = [],[]

        tmp = self.jdsoup.find("p","publish_time")
        if tmp:
            res.append(re.sub(u"职位诱惑[:：\s　]+","",tmp.findPrevious("p").get_text()))

        pos = list(self.START_BENEFIT.finditer(self.jdstr))
        if pos:
            linelist = [re.sub("[\s　]+"," ",line.strip()) for line in self.SPLIT_LINE.split(self.jdstr[pos[-1].span()[1]:]) if len(line)>3]

        linelist = filter(lambda x:len(x)>2,linelist)
        for i in range(len(linelist)):
            line = linelist[i]
            if re.match(u"\d[、\.\s]|[（\(]?[a-z\d][\.、\s][\u25cf\ff0d]",line) or self.BENEFIT.search(line) or self.clf.predict(line)=='benefit':
                res.append(line)
            elif i<len(linelist)-1 and self.clf.predict(linelist[i+1])=='benefit':
                res.append(line)
            else:
                break
            if self.START_DUTY.search(line):
                break
        self.result['benefit'] = '\n'.join(res)


    def regular_other(self):
        res = []
        for line in self.linelist:
            if len(line)>5 and self.clf.predict(line)=='other':
                res.append(line)
        self.result['other'] = '\n'.join(res)


    
    def parser(self,htmlContent=None,fname=None,url=None):
        self.preprocess(htmlContent,fname,url)
        self.regular_inc_name()
        self.regular_inc_tag()
        self.regular_pubtime()
        self.regular_jobname()
        self.regular_jobtag()
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
  #        self.regular_other()
  #      assert len(self.result.keys())==19,"wrong keys"

        return self.result

    def ouput(self):
        for k,v in self.result.iteritems():
            print k
            print v


if __name__ == "__main__":
    test = JdParserLagou()
    test.parser(fname="./test_jds/lagou/lagou_100.html")
    test.ouput()


