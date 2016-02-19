#!/usr/bin/env python
# coding=utf-8

import sys,re,codecs,jieba
from bs4 import BeautifulSoup
from urllib2 import urlopen
from collections import OrderedDict
from base import JdParserTop

reload(sys)
sys.setdefaultencoding('utf-8')


class JdParserLagou(JdParserTop):
    """
    对lagou Jd 结合html 进行解析
    """
    def __init__(self):
        JdParserTop.__init__(self)
        self.result = OrderedDict()
        self.result_inc = OrderedDict()
        self.result_job = OrderedDict()
        


    def preprocess(self,htmlContent=None,fname=None,url=None):
        self.result.clear()
        self.result_inc.clear()
        self.result_job.clear()
        self.result["jdFrom"] = "lagou"


        html = ""
        if url!=None:
            html = urlopen(url).read()
        elif htmlContent:
            html = htmlContent
        elif fname:
            html = codecs.open(fname,'rb','utf-8').read()
       
        
        self.html= re.sub(u"<br./?./?>|<BR.?/?>|<br>",u"。",html)
        soup = BeautifulSoup(self.html)

        self.jdsoup = soup.find("dl","job_detail")
        self.compsoup = soup.find("dl","job_company")
        self.jdstr = self.jdsoup.find("dd","job_bt").get_text().strip()

        self.linelist = [ line.strip() for line in self.SPLIT_LINE.split(self.jdstr) if len(line)>2]
    
    
    def regular_inc_name(self):
        link = self.compsoup.find("dt").find("img",{"class":"b2"})
        res = ""
        if ('alt' in dict(link.attrs)):
            incname1 = link['alt']
            res = incname1
        else:
            res = self.compsoup.find("dt").find("h2","fl").get_text().split()[0]
        self.result_inc["incName"] = res



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
        self.result_inc.update(res)


    def regular_pubtime(self):
        """
        发布时间 & 截止时间
        """
        pub_time = self.jdsoup.find("p","publish_time").get_text().split()[0]
        self.result["pubTime"] = pub_time



    def regular_jobname(self):
        jobname = self.jdsoup.find("dt","clearfix join_tc_icon").find('h1').get_text().split()[-1]
        self.result_job['jobPosition'] = self.clean_jobname(jobname.strip())


    def regular_jobtag(self):
        """
        返回职位性质，职位类别，招聘人数
        """
        res = {"jobType":"全职","jobCate":"","jobNum":""}

        res["jobType"] = self.jdsoup.find("dd","job_request").find_all("span")[-1].get_text()
        find_jobtype = re.search(u"实习|兼职",self.result_job["jobPosition"])
        if find_jobtype:
            res["jobType"] = find_jobtype.group()
        self.result_job.update(res)


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

        self.result_job['gender'] = str(res)


    def regular_age(self):
        """
        (minage,maxage)
        """ 
        agestr = ""
        for line in self.linelist:
            if re.search(u"\d+后",line):continue
            if self.AGE.search(line):
                findage = re.search(u"(\d{2}[\-－到至])?\d{2}岁|(至少|不低于|不超过|不大于|大概|大约|不少于|大于)?\d+周?岁|\d+周岁(以上|左右|上下)",line)
                if findage:
                   agestr = findage.group()
                   break

        self.result_job['age'] = agestr


    def regular_major(self):
        res = set()
        for line  in self.linelist:
            for word in jieba.cut(line):
                if len(word)>1 and word.lower() in self.majordic:
                    res.add(word.lower())

        self.result_job["jobMajorList"] = list(res)



    def regular_degree(self):
        degree =  self.jdsoup.find("dd","job_request").find_all("span")[3].get_text().strip()
        self.result_job['jobDiploma'] = degree



    def regular_exp(self):

        find_exp =  self.jdsoup.find("dd","job_request").find_all("span")[2]
        expstr = find_exp.get_text() if find_exp else "None"
        self.result_job['jobWorkAge'] = expstr
    

    def regular_skill(self):
        res = {}
        for line in self.linelist:
            for word in jieba.cut(line):
                if len(word)>1 and word.lower() in self.skilldic:
                    res[word.lower()] = res.get(word.lower(),0) + 1

        sorted_res = sorted(res.items(), key = lambda d:d[1], reverse=True)

        res = [ word for (word,cnt) in sorted_res[:5] ]
        self.result_job["skillList"] = res



    def regular_workplace(self):
        workplace =  self.jdsoup.find("dd","job_request").find_all("span")[1].get_text().strip()
        self.result_job['jobWorkLoc'] = workplace



    def regular_pay(self):
        paystr =  self.jdsoup.find("dd","job_request").find_all("span")[0].get_text().strip()
        if paystr:
            self.result_job['jobSalary'] = paystr


    
    def regular_cert(self):
        res = []
        for line in self.linelist:
            findcert = self.CERT.search(line)
            if findcert and len(findcert.group())<6 and not re.search(u"保证",findcert.group()):
                res.append(findcert.group())
            else:
                findcert = re.search(u"有(.+资格证)",line)
                if findcert:
                    res.append(findcert.group(1))

        res = re.sub(u"[或及以上]","",'|'.join(res))
        self.result_job['certList'] = res.split('|')

    

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

        self.result_job['workDemand'] = '\n'.join(res)


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

        self.result_job['workDuty'] = '\n'.join(res)


    def regular_benefit(self):
        
        res = []
        tmp = self.jdsoup.find("p","publish_time")
        if tmp:
            res.append(re.sub(u"职位诱惑[:：\s　]+","",tmp.findPrevious("p").get_text()))

        self.result_job['jobWelfare'] = '\n'.join(res)


    def regular_other(self):
        self.result_job["jobDesc"] = self.jdstr
        self.result["jdInc"] = self.result_inc
        self.result["jdJob"] = self.result_job

    
    def parser_basic(self,htmlContent=None,fname=None,url=None):
        """
        只做基本抽取，保证99%以上正确
        """
        self.preprocess(htmlContent,fname,url)
        self.regular_inc_name()
        self.regular_inc_tag()
        self.regular_pubtime()
        self.regular_jobname()
        self.regular_jobtag()
        self.regular_degree()
        self.regular_exp()
        self.regular_pay()
        self.regular_benefit()
        self.regular_workplace()
        self.regular_other()

        return self.result




    def parser_detail(self,htmlContent=None,fname=None,url=None):
        """
        进一步进行简单的语义信息抽取，争取90％以上准确率
        """
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
        self.regular_other()
        
        return self.result




    def ouput(self):
        for k,v in self.result.iteritems():
            print k
            print v

if __name__ == "__main__":
    import json 

    test = JdParserLagou()
    url = "http://www.lagou.com/jobs/1018301.html"
    result1 = test.parser_basic(url=url)
    print json.dumps(result1,ensure_ascii=False,indent=4)
   
    print 'detail'
    result2 = test.parser_detail(url = url)
    print json.dumps(result2,ensure_ascii=False,indent=4)
    

