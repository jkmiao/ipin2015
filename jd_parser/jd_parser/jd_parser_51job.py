#!/usr/bin/env python
# coding=utf-8

import sys,re,codecs,jieba
from bs4 import BeautifulSoup
from urllib2 import urlopen
from collections import OrderedDict,Counter
from base import JdParserTop
import logging

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig()

class JdParser51Job(JdParserTop):
    """
    对lagou Jd 结合html 进行解析
    """
    def __init__(self):
        JdParserTop.__init__(self)
        self.result = OrderedDict()

    def preprocess(self,htmlContent=None,fname=None,url=None):
        self.result.clear()
        if url!=None:
            html = urlopen(url).read().decode('gb18030')
        elif htmlContent:
            html = htmlContent 
        elif fname:
            html = codecs.open(fname,"rb",'gb18030').read()

        if len(html)<60:
            raise Exception("input arguments error")

        self.html= re.sub(u"<br./?./?>|<BR.?/?>|<br>",u"。",html)
        self.soup = BeautifulSoup(self.html,"lxml")

        self.jdsoup = self.soup.find("div","tCompany_introduction")
        self.compsoup = self.soup.find("div","tBorderTop_box job_page_company")
        self.lineDl = self.jdsoup.find("div","tCompany_basic_job").find_all("dl","lineDl") # 为了方便取出表格基本信息


        self.jdstr = self.jdsoup.find("div","tCompany_text").get_text()
     #  self.jdstr = self.CLEAN_TEXT.sub(" ",jdstr)

        self.linelist = [ line.strip() for line in self.SPLIT_LINE.split(self.jdstr) if len(line.strip())>3]
    
    
    def regular_incname(self):
        incname=""
        if self.compsoup:
            incname = self.compsoup.find('h2').get_text()
        self.result['incName'] = incname.strip()


    def regular_inc_tag(self):
        res = {"incUrl":"","incIntro":"","incType":"","incLocation":"","incIndustry":"","incScale":""}
        if not self.compsoup:
            self.result.update(res)
            return 
            
        inc_tags = self.compsoup.find_all("dl","lineDl")

        for tag in inc_tags:
            key = tag.find('dt').get_text()
            if re.search(u"行业",key):
                res["incIndustry"] = tag.find("dd").get_text().strip()
            elif re.search(u"性质",key):
                res["incType"]=tag.find("dd").get_text().strip()
            elif re.search(u"规模",key):
                res["incScale"] = tag.find("dd").get_text().strip()
            elif re.search(u"地址",key):
                res["incLocation"] = tag.find("p",{"class":"job_company_text"}).get_text().strip()
            elif re.search(u"公司网站",key):
                res["incUrl"] = tag.find("dd").get_text().strip()

        if re.search(u"公司介绍",self.html) and self.soup.find("div","tCompany_text_gsjs"):
            res["incIntro"] = self.soup.find("div","tCompany_text_gsjs").get_text().strip()

            incUrl = self.INC_URL.search(res["incIntro"])
            if not res["incUrl"] and incUrl:
                res["incUrl"] = re.search("[\w\d\./_:\-]+",incUrl.group()).group()
        self.result.update(res)
        

    def regular_pubtime(self):
        """
        发布时间 & 截止时间
        """
        pub_time = self.jdsoup.find("div","tCompany_basic_job").dd.get_text()
        self.result["pub_time"] = pub_time
        self.result["end_time"] = ""



    def regular_jobname(self):
        jobname = self.jdsoup.find("li","tCompany_job_name").find('h1').get_text()
#        self.result['jobName'] = re.sub(u"(职位编号：\d+)|\s","",jobname.strip().lower())
        jobname = self.CLEAN_JOBNAME.sub("",jobname.strip().lower())


    def regular_job_tag(self):
        res = {"jobCate":'',"jobType":'全职',"jobNum":"0"}
        for line in self.lineDl:
            for tag in line.find_all("dt"):
                if re.search(u"招聘人数",tag.get_text()):
                    res["jobNum"] = tag.findNext("dd").get_text().strip()

        for line in self.lineDl:
            if re.search(u"职能类别",line.dt.get_text()):
                res["jobCate"] =  " | ".join(line.dd.get_text().split())
            if re.search(u"职位标签",line.dt.get_text()):
                if re.search(u"实习|兼职",line.dd.get_text()):
                    res["jobType"] = u"实习"
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
                findage = re.search(u"\d{2}?\s?[\-－　到至\s]?\d{2}周?岁|(至少|不低于|不超过|不大于|大概|大约|不少于|大于)\d+周?岁|\d+周岁(以上|左右|以下)|年龄.{2,9}",line)
                if findage:
                    agestr = findage.group()
                    age = re.findall(u"\d{1,2}",agestr)
                    if len(age)>1:
                        res[0],res[1] = age[0],age[1]
                    elif len(age)==1:
                        if re.search(u"以上|不低于|至少|大于|超过",line):
                            res[0] = age[0]
                        elif re.search(u"小于|低于|不超过|不得?高于|以下|不大于",line):
                            res[1] = age[0]
                        else:
                            res[0] = int(age[0])-3
                            res[1] = int(age[0])+3
                    break
        self.result['age'] = map(str,res)


    def regular_major(self):
        res = []
        for line in self.linelist:
            for word in jieba.cut(line):
                if word.lower() in self.majordic or word[:-2] in self.majordic:
                    res.append(word)
        if not res:
            res = ['0']
        self.result["major"] = list(set(res))



    def regular_degree(self):
        res = ""
        line = self.lineDl[1] 
        for tag in line.find_all("dt"):
            if re.search(u"学历要求",tag.get_text()):
                res = tag.findNext("dd").get_text()
                break
        for w in jieba.cut(res):
            if w in self.degreedic:
                res = w
                break
        self.result['degree'] = res



    def regular_exp(self):
        res = [0,100]
        expstr =""
        for line in self.lineDl:
            if re.search(u"工作年限",line.dt.get_text()):
                expstr = line.dd.get_text().strip()
                break
        exp = re.findall("\d+",expstr)

        if len(exp)==1:
            res[0]= exp[0]
        elif len(exp)>1:
            res[0],res[1] = exp[0],exp[1]

#        elif re.search(u"应届",expstr):
#                res = u"应届生"

        self.result['exp'] = map(str,res)    


    def regular_skill(self):
        res = []
        for line in self.lineDl:
            for tag in line.find_all("dt"):
                if re.search(u"语言要求",tag.get_text()):
                    res.append(tag.findNext("dd").get_text().strip())
                    break

        for line in self.linelist:
            for word in jieba.cut(line):
                word = word.lower()
                if word in self.skilldic:
                    res.append(word)
        res =[w[0] for w in Counter(res).most_common(5)]
        self.result["skill"] = res



    def regular_workplace(self):
        res = ""
        
        for line in self.lineDl:
            for tag in line.find_all("dt"):
                if re.search(u"工作地点",tag.get_text()):
                    res = tag.findNext("dd").get_text()
                    break

        self.result['workplace'] = res



    def regular_pay(self):
        paystr = ""
        res = [0,0]
        for line in self.lineDl:
            for tag in line.find_all("dt"):
                if re.search(u"薪资范围",tag.get_text()):
                    paystr = tag.findNext("dd").get_text()
                    break
        if paystr:
            pay = map(lambda x: re.sub("[ＫkK]","000",x),re.findall("\d+[kK]?",paystr))
            if len(pay)==1:
                res[0] = pay[0]
            elif len(pay)>1:
                res[0],res[1] = pay[0],pay[-1]

        if re.search(u"万|年薪",paystr):
            res = [ int(res[i])*10000/12 for i in range(len(res))]
        
        self.result['pay'] = map(str,res)

    
    
    def regular_cert(self):
        res = []
        for line in self.linelist:
            findcert = self.CERT.search(line)
            if findcert:
                res.append(findcert.group())
            else:
                findcert = re.search(u"有(.+资格)",line)
                if findcert:
                    res.append(findcert.group(1))
        res = re.sub(u"[通过或以上至少]","","|".join(res))
        self.result['cert'] = res.split("|")


    def regular_demand(self):
        """
        岗位要求
        """

        jdstr = self.jdstr
        res,linelist = [],[]
        pos = list(self.START_DEMAND.finditer(jdstr))
        if pos:
            linelist = [line.strip() for line in self.SPLIT_LINE.split(jdstr[pos[-1].span()[1]:]) if line.strip()>3]

        linelist = filter(lambda x:len(x)>2,linelist)
        for i in range(len(linelist)):
            line = linelist[i]
            if self.START_DEMAND.search(line):
                continue
            if self.START_DUTY.search(line):
                break
            if re.match(u"\d[\.、\s　]|[\(（【][a-z\d][\.、\s　]|[\u25cf\uff0d\u2022]",line) or self.DEMAND.search(line) or self.clf.predict(line)=="demand":
                res.append(self.CLEAN_LINE.sub("",line))
            elif i<len(linelist)-1 and self.clf.predict(linelist[i+1])=="demand":
                res.append(self.CLEAN_LINE.sub("",line))
            else:
                break
        if not res:
            for line in self.linelist:
                if self.clf.predict(line) == "demand":
                    res.append(self.CLEAN_LINE.sub("",line))

        res = [str(i+1)+". "+line for i,line in enumerate(res)]
        self.result["demand"] = '\n'.join(res)

    
    def regular_duty(self):
        """
        岗位职责
        """
        jdstr = self.jdstr
        res,linelist = [],[]
        pos = list(self.START_DUTY.finditer(jdstr))
        if pos:
            linelist = [line.strip() for line in self.SPLIT_LINE.split(jdstr[pos[-1].span()[1]:]) if line.strip()>3]

        linelist = filter(lambda x:len(x)>2,linelist)
        for i in range(len(linelist)):
            line = linelist[i]
            if self.START_DUTY.search(line):
                continue
            if self.START_DEMAND.search(line):
                break

            if re.match(u"\d[\.、\s　]|[\(（【][a-z\d][\.、\s　]|[\u25cf\uff0d]",line) or self.DUTY.search(line) or self.clf.predict(line)=="duty":
                res.append(self.CLEAN_LINE.sub("",line))
            elif i<len(linelist)-1 and self.clf.predict(linelist[i+1])=="duty":
                res.append(self.CLEAN_LINE.sub("",line))
            else:
                break
        if not res:
            for line in self.linelist:
                if self.clf.predict(line) == "duty":
                    res.append(self.CLEAN_LINE.sub("",line))
        res = [str(i+1)+". "+line for i,line in enumerate(res)]
        self.result["duty"] = '\n'.join(res)




    def regular_benefit(self):

        jdstr = self.jdstr
        res,linelist = [],[]

        for line in self.lineDl:
            if re.search(u"薪酬福利",line.find("dt").get_text()):
                res.append(line.find("dd").get_text().strip())

        pos = list(self.START_BENEFIT.finditer(jdstr))
        if pos:
            linelist = [re.sub(u"[\s　]+"," ",line.strip()) for line in self.SPLIT_LINE.split(jdstr[pos[-1].span()[1]:]) if line>3]

        linelist = filter(lambda x:len(x)>2,linelist) 
        for i in range(len(linelist)):
            line = linelist[i]
            if re.match(u"\d[\.、\s　]|[\(（【][a-z\d][\.、\s　]|[\u25cf\uff0d]",line) or self.BENEFIT.search(line) or self.clf.predict(line)=="benefit":
                res.append(self.CLEAN_LINE.sub("",line))
            else:
                break
            if self.START_DUTY.search(line) or self.clf.predict(line)=='other':
                break

        self.result["benefit"] = '\n'.join(set(list(res)))

    def regular_other(self):

        res = []
        jdstr = self.jdstr
        linelist = [ self.clean_line(line) for line in self.SPLIT_LINE.split(jdstr) if len(line.strip())>5]
        for line in linelist:
            if len(line)<3:continue
            if self.clf.predict(line)=='other':
                res.append(line)
        
        self.result['other'] = '\n'.join(res)
                
    
    
    
    def parser(self,htmlContent="",fname=None,url=None):
        try:
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
        except Exception,e:
            print '51job error',e


        return self.result




    def ouput(self):
        for k,v in self.result.iteritems():
            print k
            if isinstance(v,list):
                print '['+','.join(v)+']'
            else:
                print v
            print "-"*20


if __name__ == "__main__":
    import os
    test = JdParser51Job()
    path = './test_jds/51job/'
    fnames = [ path+file for file in os.listdir(path)][:10]
    test.parser(url="http://jobs.51job.com/beijing/74160122.html")
    print test.ouput()

    for fname in fnames:
        print "=="*20,fname
        htmlContent = codecs.open(fname,'rb','gb18030').read()
        test.parser(htmlContent,fname=None,url=None)
        test.ouput()
        print ""


