#!/usr/bin/env python
# coding=utf-8

import sys,re,codecs,jieba
from bs4 import BeautifulSoup
from urllib2 import urlopen
from collections import OrderedDict,Counter
from base import JdParserTop
reload(sys)
sys.setdefaultencoding('utf-8')


class JdParser58tc(JdParserTop):
    """
    对58 同城 html 进行jd解析
    """
    def __init__(self):
        JdParserTop.__init__(self)
        self.result = OrderedDict()
        self.result_inc = OrderedDict()
        self.result_job = OrderedDict()


    def preprocess(self,htmlContent,fname=None,url=None):
        """
        预处理，改换换行符等
        """
        self.result.clear()
        self.result_inc.clear()
        self.result_job.clear()
        self.result["jdFrom"] = "58tongcheng"


        html = ""
        if url!=None:
            html = urlopen(url).read()
        elif htmlContent:
            html = htmlContent
        elif fname:
            html = open(fname).read()
        
        if len(html)<60:
            raise Exception("input arguments error")
        
        self.html= re.sub(u"<br.?/?>|<BR.?/?>|<br>",u"\n",html)

        self.soup = BeautifulSoup(self.html,"lxml")

        self.jdsoup = self.soup.find("div","wb-main").find("div","posCont")
        self.compsoup = self.jdsoup.find("div","posSum")

        self.jdbasic_soup = self.jdsoup.find("div","xq").find_all("li","condition") if self.jdsoup.find("div","xq") else []


        jdstr = self.jdsoup.find("div",{"id":"zhiwei"})
        self.jdstr = jdstr.find("div","posMsg borb").get_text().strip() if jdstr else ""

        self.linelist = [ line.strip() for line in self.SPLIT_LINE.split(self.jdstr) if len(line)>1]
    


    def regular_incname(self):
        find_incname_soup = self.compsoup.find("a","companyName")
        self.result_inc["incName"] = find_incname_soup.get_text().strip() if find_incname_soup else "None"
        self.result_inc["incUrl"] = find_incname_soup.get("href","") if find_incname_soup else "None"



    def regular_inc_tag(self):
        res = {"incUrl":self.result_inc["incUrl"],"incIntro":""}
        find_comptag = self.compsoup.find("div","compMsg clearfix")
        if not find_comptag:
            self.result_inc.update(res)
            return 

        inc_tags = find_comptag.find("ul").find_all("li") if find_comptag.find("ul") else []
        for tag in inc_tags:
            key = tag.find("span").get_text()
            if re.search(u"行业",key):
                res['incIndustry'] = re.sub(u"行业：|\s","",tag.get_text().strip())

            elif re.search(u"性质",key):
                res["incType"] = re.sub(u"性质：|\s","",tag.get_text().strip())

            elif re.search(u"规模",key):
                res["incScale"] = re.sub(u"规模：|\s","",tag.get_text().strip())

            elif re.search(u"地址",key):
                res["incLocation"] = re.sub(u"查看公司地图|[\s　]|地址：","",tag.get_text().strip())

        find_inc_intro = self.soup.find("div",{"class":"compIntro","id":"gongsi"})

        if find_inc_intro and find_inc_intro.find("p"):
            res["incIntro"] = find_inc_intro.find("p").get_text().strip()

        if len(res["incUrl"])<3 and res["incIntro"]:
            find_url = self.INC_URL.search(res["incIntro"])
            if find_url:
                res["incUrl"] = re.search(u"[\d\w\.:/_\-]+",find_url.group()).group()

        self.result_inc.update(res)




    def regular_pubtime(self):
        """
        发布时间 & 截止时间
        """
        find_pubtime = self.jdsoup.find("div","headCon")
        if find_pubtime:
            self.result["pubTime"] = find_pubtime.find("li").find_next("span").get_text().strip()
        

        if "pubTime" not in self.result:
            self.result["pubTime"] = ""



    def regular_jobname(self):

        jobname = self.jdsoup.find('h1').get_text() if self.jdsoup.find("h1") else "None"
        self.result_job['jobPosition'] = re.sub("\s+","",jobname.strip().lower())


    def regular_job_tag(self):

        res = {"jobCate":"",'jobType':"全职","jobNum":""}

        if self.jdbasic_soup:
            for li in self.jdbasic_soup:
                if re.search(u"工作性质",li.span.get_text()):
                    res["jobType"] = li.get_text()
                elif re.search(u"招聘人数|职位",li.span.get_text()):
                    find_jobnum =  re.search(u"\d+-\d+人|\d+人",li.get_text())
                    if find_jobnum:
                        res['jobNum'] = find_jobnum.group()
                elif re.search(u"类别",li.span.get_text()):
                    res["jobCate"] = li.get_text()

        find_job_type = re.search(u"实习|兼职",self.result_job["jobPosition"])
        if find_job_type:
            res["jobType"] = find_job_type.group()

        self.result_job.update(res)

    def regular_sex(self):
        """
        @return: 不限, 男, 女
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
        agestr = u"不限"
        for line in self.linelist:
            if re.search(u"\d+后",line):continue
            if self.AGE.search(line):
                findage = re.search(u"\d{2}?\s?[\-　－到至]?\s?\d{2}周?岁|(至少|不低于|不超过|不大于|大概|大约|不少于|大于)\d+周?岁|\d+周岁(以上|左右|上下)",line)
                if findage:
                    agestr = findage.group()

        self.result_job['age'] = agestr


    def regular_major(self):
        res = []
        for line in self.linelist:
            for word in jieba.cut(line):
                if word in self.majordic:
                    res.append(word)
            if res:
                break

        self.result_job["jobMajorList"] = list(set(res))



    def regular_degree(self):
        degree = ""
        if self.jdbasic_soup:
            for li in self.jdbasic_soup:
                if re.search(u"学历要求",li.get_text()):
                    degree = re.sub(u"学历要求：|\s","",li.find("div","fl").get_text().strip())

        self.result_job['jobDiploma'] = degree



    def regular_exp(self):

        expstr = ""
        if self.jdbasic_soup:
            for li in self.jdbasic_soup:
                if re.search(u"工作年限",li.get_text()):
                    expstr = re.sub(u"工作年限：|\s","",li.find("div","fl").get_text())
                    break
        self.result_job['jobWorkAge'] = expstr
    

    def regular_skill(self):
        res = []
        for line in self.linelist:
            for word in jieba.cut(line):
                word = word.lower()
                if word in self.skilldic:
                    res.append(word)
        res =[w[0] for w in Counter(res).most_common(5)]
        self.result_job["skillList"] = res



    def regular_workplace(self):
        locstr = ""
        if self.jdbasic_soup:
            for li in self.jdbasic_soup:
                if re.search(u"地址",li.span.get_text()):
                    locstr = li.find_all("span",limit=3)[1].get_text().strip()
                    break
        
        self.result_job['jobWorkLoc'] = re.sub("\s","",locstr)



    def regular_pay(self):
        
        paystr = ""
        if self.jdbasic_soup:
            for li in self.jdbasic_soup:
                if re.search(u"薪资|薪酬",li.span.get_text()):
                    paystr = li.find_next("span","salaNum").get_text()
                    break

        self.result_job['jobSalary'] = paystr.strip()

    
    def regular_cert(self):
        res = []
        for line in self.linelist:
            findcert = self.CERT.search(line)
            if findcert and len(findcert.group()) and not re.search(u"保证",findcert.group())<5:
                res.append(findcert.group())
            else:
                findcert = re.search(u"有(.+资格证)",line)
                if findcert:
                    res.append(findcert.group())
        res = re.sub(u"[通过或以上至少]","","|".join(res))
        self.result_job['certList'] = res.split("|")

    


    def regular_demand(self):
        
        jdstr = self.jdstr
        res,linelist = [],[]
        pos = list(self.START_DEMAND.finditer(jdstr))
        if len(pos)>0:
            linelist = [line.strip() for line in self.SPLIT_LINE.split(jdstr[pos[-1].span()[1]:]) if line>3]

        linelist = filter(lambda x:len(x)>2,linelist) 
        for i in range(len(linelist)):
            line = linelist[i]
            if self.START_DUTY.search(line):
                break
            if re.match(u"\d[、.\s ]|[（\(【][a-z\d][\.、\s ]|[\u25cf\uff0d]",line) or self.DEMAND.search(line) or self.clf.predict(line)=="demand":
                res.append(self.CLEAN_LINE.sub("",line))
            elif i<len(linelist)-1 and self.clf.predict(linelist[i+1])=='demand':
                res.append(self.CLEAN_LINE.sub("",line))
            else:
                break

        if not res:
            linelist = [ line.strip() for line in self.SPLIT_LINE.split(jdstr) if len(line.strip())>5]
            for line in linelist:
                if self.clf.predict(line)=='demand':
                    res.append(self.CLEAN_LINE.sub("",line))

        res = [ str(i)+". "+line for i,line in enumerate(res,1) ]
        self.result_job['workDemand'] = '\n'.join(res)

    def regular_duty(self):

        jdstr = self.jdstr
        res,linelist = [],[]
        pos = list(self.START_DUTY.finditer(jdstr))
        if len(pos)>0:
            linelist = [ line.strip() for line in self.SPLIT_LINE.split(jdstr[pos[-1].span()[1]:]) if line.strip()>3]
        linelist = filter(lambda x:len(x)>2,linelist) 
        for i in range(len(linelist)):
            line = linelist[i]
            if self.START_DUTY.search(line):
                continue
            if self.START_DEMAND.search(line) or self.DEMAND.search(line):
                break
            if re.match(u"^\d[、.\s ]|[（\(]?[a-z\d][\.、\s ]|[\u25cf\uff0d]",line) or self.DUTY.search(line) or self.clf.predict(line)=="duty":
                res.append(self.CLEAN_LINE.sub("",line))
            elif i<len(linelist)-1 and self.clf.predict(linelist[i+1])=='duty':
                res.append(self.CLEAN_LINE.sub("",line))
            else:
                break
        if not res:
            linelist = [ self.CLEAN_LINE.sub("",line) for line in self.SPLIT_LINE.split(jdstr) if len(line.strip())>5]
            for line in linelist:
                if self.clf.predict(line)=='duty':
                    res.append(self.CLEAN_LINE.sub("",line))
        res = [ str(i)+". "+line for i,line in enumerate(res,1) ]
        self.result_job['workDuty'] = '\n'.join(res)



    def regular_benefit(self):

        res = []
       
        benefit_tags = []
        find_benefit = self.jdsoup.find("div","xq").find("li","condition hierarchy")
        if find_benefit:
            benefit_tags = find_benefit.find_all("li")
        
        for tag in benefit_tags:
            if tag.find("span"):
                res.append(tag.find("span").get_text().strip())

        self.result_job['jobWelfare'] = '\n'.join(res)


    def regular_other(self):
        jdstr = self.jdstr.strip()
        self.result_job['jobDesc'] = jdstr 
        
        self.result["jdInc"] = self.result_inc
        self.result["jdJob"] = self.result_job

    
    def parser_basic(self,htmlContent=None,fname=None,url=None):
        self.preprocess(htmlContent,fname,url)
        self.regular_incname()
        self.regular_inc_tag()
        self.regular_pubtime()
        self.regular_jobname()
        self.regular_job_tag()
        self.regular_pay()
        self.regular_degree()
        self.regular_exp()
        self.regular_workplace()
        self.regular_benefit()
        self.regular_other()

        return self.result

    

    def parser_detail(self,htmlContent=None,fname=None,url=None):
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
        self.regular_other()
        
        return self.result


    def ouput(self):
        for line in self.linelist:
            print line

        for k,v in self.result.iteritems():
            print  k
            print v


if __name__ == "__main__":
    import os,json

    test = JdParser58tc()
    path = './test_jds/58tc/'
    fnames = [ path + fname for fname in os.listdir(path) if fname.endswith(".html")]
    for fname in fnames:
        print '=='*20,fname
        htmlContent = codecs.open(fname,'rb','utf-8').read()

        result1 = test.parser_basic(htmlContent,fname=None,url=None)
        print json.dumps(result1,ensure_ascii=False,indent=4)

        print 'detail'
        result2 = test.parser_detail(htmlContent)
        print json.dumps(result2,ensure_ascii=False,indent=4)

