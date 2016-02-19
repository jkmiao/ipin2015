#!/usr/bin/env python
# coding=utf-8

import sys,re,codecs,jieba
from bs4 import BeautifulSoup
from urllib2 import urlopen
from collections import OrderedDict 
from base import JdParserTop

reload(sys)
sys.setdefaultencoding('utf-8')


class JdParserLiePin(JdParserTop):
    """
    对liepin Jd 结合html 进行解析
    """
    def __init__(self):
        JdParserTop.__init__(self)
        self.result = OrderedDict()
        self.result_inc = OrderedDict()
        self.result_job = OrderedDict()


    def preprocess(self,htmlContent,fname=None,url=None):
        self.result.clear()
        self.result_inc.clear()
        self.result_job.clear()

        self.result["jdFrom"] = "liepin"

        html = ""
        if url!=None:
            html = urlopen(url).read().decode("utf-8")
        elif htmlContent:
            html = htmlContent
        elif fname:
            html = open(fname).read().decode(u"utf-8")
        
        if len(html)<60:
            raise Exception("input arguments error")
        
        if re.search(u"职务发布者|猎头等级|服务好评率",html):
            self.lietou = 1  # 猎头发布
        else:
            self.lietou = 0  # 企业发布


        
        self.html= re.sub(u"<br.?/?>|<BR.?/?>|<br>",u"\n",html)

        self.soup = BeautifulSoup(self.html)

        self.jdsoup = self.soup.find("div","title")
        if self.lietou:
            self.compsoup = BeautifulSoup()
        else:
            self.compsoup = self.soup.find("div","side").find("div","right-post-top")

        self.jdstr = self.jdsoup.find("div","content content-word").get_text().strip()
        self.linelist = [ line.strip() for line in self.SPLIT_LINE.split(self.jdstr) if len(line)>1]
    
        # 针对基本信息，提前存储，方便解析基本字段
        self.jdtop_soup = self.jdsoup.find("div","job-main").find("div","job-title-left")
        self.jdtop2_soup = self.jdsoup.find("div","job-main").find("div","job-title-left").find("div","resume clearfix").find_all("span")
        



    def regular_incname(self):
        if not self.lietou and self.compsoup:
            find_inc_name = self.compsoup.find('p',"post-top-p")
            if find_inc_name:
                self.result_inc['incName'] = find_inc_name.get_text().strip()
                if find_inc_name.find("a"):
                    self.result_inc["incUrl"] = find_inc_name.find("a").get("href","None")
        elif self.lietou:
            find_incname = self.jdsoup.find("div","title-info").find('h3')
            if find_incname:
                self.result_inc["incName"] = find_incname.get_text().strip()




    def regular_inc_tag(self):
        res = {"incIntro":"None"}
            
        if self.lietou == 0 :
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

        find_inc_intro = self.jdsoup.find("h3",text=re.compile(u"企业介绍"))
        if find_inc_intro:
            res["incIntro"] = find_inc_intro.find_next("div","content").get_text().strip()
        self.result_inc.update(res)



    def regular_pubtime(self):
        """
        发布时间 & 截止时间
        """
        pub_time = self.jdtop_soup.find("p","basic-infor").find_all("span")[1].get_text()
        self.result["pubTime"] = re.sub(u"[:：　\s\n]|发布于","",pub_time)



    def regular_jobname(self):
        jobname = self.jdsoup.find("div","title-info").find('h1').get_text()
        self.result_job['jobPosition'] = self.CLEAN_JOBNAME.sub("",jobname)


    def regular_job_tag(self):
        res = {"jobCate":"",'jobType':"全职","jobNum":""}
        if re.search(u"实习",self.result_job["jobPosition"]):
            res["jobType"]=u"实习"
        
        self.result_job.update(res)




    def regular_sex(self):
        jdbasic_soup = self.jdsoup.find("h3",text=re.compile(u"其他信息")).find_next("div","content").find_all("li")
        for line in jdbasic_soup:
            key,value = re.split(u"[:：]",line.get_text())
            if re.search(u"性别",key):
                self.result_job["gender"] = value.strip()
                break

    
    def regular_sex_detail(self):
        res = ""
        jdbasic_soup = self.jdsoup.find("h3",text=re.compile(u"其他信息")).find_next("div","content").find_all("li")
        for line in jdbasic_soup:
            key,value = re.split(u"[:：]",line.get_text())
            if re.search(u"性别",key):
                if re.search(u"性别不限|男女不限|不限",value):
                    res = u"不限"
                elif re.search(u"男",value):
                    res = u"男"
                elif re.search(u"女",value):
                    res = u"女"
                break

        if not res:
            for line in self.linelist:
                find_sex = re.search(u"男|女|性别不限",line)
                if find_sex:
                    res = find_sex.group()
                    break
        if not res:
            res = u"不限"
        self.result_job["gender"] = str(res)


    def regular_age(self):
        """
        [minage,maxage]
        """ 
        agestr = self.jdtop2_soup[-1].get_text()

        self.result_job['age'] = agestr



    def regular_major(self):
        # 由others处定义

        self.result_job["jobMajorList"] = [u"不限"]


    def regular_degree(self):
        degree = self.jdtop2_soup[0].get_text().strip()
        self.result_job['jobDiploma'] = degree



    def regular_exp(self):

        expstr = self.jdtop2_soup[1]
        self.result_job['jobWorkAge'] = expstr.get_text().strip() if expstr else "None"
    

    def regular_skill(self):
        res = {}
        for line in self.linelist:
            for word in jieba.cut(line):
                word = word.strip().lower()
                if word in self.skilldic:
                    res[word] = res.get(word,0) + 1
        sorted_res = sorted(res.items(),key=lambda d:d[1],reverse=True)
        res = [ word for word,count in sorted_res[:5] ]

        self.result_job["skillList"] = res


    def regular_language(self):
        #　语言要求
        res = ""
        res = self.jdtop2_soup[2].get_text().strip()
        self.result_job["language"] = res
        

    def regular_workplace(self):
        res = self.jdtop_soup.find("p","basic-infor").find("span").get_text().strip()        
        self.result_job['jobWorkLoc'] = res



    def regular_pay(self):
        paystr = self.jdtop_soup.find("p","job-main-title").get_text()
        self.result_job['jobSalary'] = re.sub(u"\s+|\d+小时反馈|\d+天内?反馈|查看率.+|反馈率.+","", paystr.strip())
        
        find_pay_tag = self.jdsoup.find("h3",text=re.compile(u"薪酬福利"))
        others = {}
        if find_pay_tag:
            pay_tags = find_pay_tag.find_next("div","content").find_all("li")

            for line in pay_tags:
                key,value = re.split(u"：",line.get_text())
                if re.search(u"职位年薪",key):
                    others["yearSalary"] = value.strip()
                elif re.search(u"薪资构成",key):
                    others["salaryCombine"] = value.strip()
                elif re.search(u"年假福利",key):
                    others["holidayWelfare"] = value.strip()
                elif re.search(u"社保福利",key):
                    others["socialWelfare"] = value.strip()
                elif re.search(u"居住福利",key):
                    others["livingWelfare"] = value.strip()
                elif re.search(u"通讯交通",key):
                    others["trafficWelfare"] = value.strip()

        self.result_job["others"] = others

    
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

        self.result_job['certList'] = res
    


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
        self.result_job['workDemand'] = '\n'.join(res)

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

        self.result_job['workDuty'] = '\n'.join(res)



    def regular_benefit(self):
        res = []
        
        job_tags = self.jdsoup.find("div","job-main").find("div","tag-list clearfix")
        if job_tags:
            job_tags = job_tags.find_all("span","tag")
            for tag in job_tags:
                res.append(tag.get_text())

        self.result_job['jobWelfare'] = '\n'.join(res)


    def regular_other(self):
        res = {}
        jdbasic_soup = self.jdsoup.find("h3",text=re.compile(u"其他信息")).find_next("div","content").find_all("li")

        for line in jdbasic_soup:
            key,value = re.split(u"[:：]",line.get_text())
            if re.search(u"所属部门",key):
                res["jobDepartment"] = value.strip()
            elif re.search(u"专业要求",key):
                self.result_job["jobMajorList"] = [value.strip()]
            elif re.search(u"汇报对象",key):
                res["jobReport"] = value.strip()
            elif re.search(u"下属人数",key):
                res["jobSubSize"] = value.strip()

            elif re.search(u"性别要求",key):
                self.result_job["gender"] = value.strip()
            elif re.search(u"所属行业",key):
                self.result_inc["incIndustry"] = value.strip()
            elif re.search(u"企业性质",key):
                self.result_inc["incType"] = value.strip()
            elif re.search(u"企业规模",key):
                self.result_inc["incScale"] = value.strip()

        self.result_job["jobDesc"] = self.jdstr
        self.result["jdInc"] = self.result_inc
        self.result["jdJob"] = self.result_job
        self.result["jdJob"]["others"] = res.copy()


    def parser_basic(self,htmlContent=None,fname=None,url=None):
        """
        页面简单抽取
        """
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
        self.regular_language()
        self.regular_workplace()
        self.regular_pay()
        self.regular_benefit()
        self.regular_other()
        
        return self.result


    def parser_detail(self,htmlContent=None,fname=None,url=None):
        """
        进一步简单的语义解析
        """
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
        self.regular_language()
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
            if isinstance(v,list):
                print "[",",".join(v),"]"
            else:
                print v



if __name__ == "__main__":
    import os,json 

    test = JdParserLiePin()
    path = './test_jds/liepin/'
    fnames = [ path+fname for fname in os.listdir(path) ]
    fnames += [ "./test_jds/liepin/liepin_1lt.html" ]
    for fname in fnames:
        print '==='*20,fname
        htmlContent = codecs.open(fname,'rb','utf-8').read()
        result1 = test.parser_basic(htmlContent,fname=None,url=None)
        print json.dumps(result1,ensure_ascii=False,indent=4)
        print "detail"
        result2 = test.parser_detail(htmlContent,url=None)
        print json.dumps(result2,ensure_ascii=False,indent=4)

