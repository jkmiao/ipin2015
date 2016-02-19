#!/usr/bin/env python
# coding=utf-8

import sys,re,codecs,jieba
from bs4 import BeautifulSoup
from urllib2 import urlopen
from collections import OrderedDict 
from base import JdParserTop

reload(sys)
sys.setdefaultencoding('utf-8')


class JdParserHighPin(JdParserTop):
    """
    对智联卓聘jd进行解析
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
        self.result_job["others"] = {}

        self.result["jdFrom"] = "highpin"

        html = ""
        if url!=None:
            html = urlopen(url).read().decode("utf-8")
        elif htmlContent:
            html = htmlContent
        elif fname:
            html = open(fname).read().decode(u"utf-8")
        
        if len(html)<60:
            raise Exception("input arguments error")
        
        
        self.soup = BeautifulSoup(html,"lxml")

        self.jdsoup = self.soup.find("div",{"id":"main"})
        self.jdtitles = self.jdsoup.find_all("h5","v-title-con")

        
        find_demandsoup = ""
        for line in self.jdtitles:
            if re.search(u"职位描述",line.get_text()):
                find_demandsoup = line
                break
        if find_demandsoup:
            self.demandsoup = find_demandsoup.find_next_sibling("div")
            self.linelist = self.demandsoup.get_text(";",strip=True).split(";")
            self.jdstr = '\n'.join(self.linelist)
        else:
            self.demandsoup = ""
            self.linelist = []
            self.jdstr = ""



    def regular_incname(self):
        # 在 regular_inc_tag 中抽取，改为对公司介绍进行抽取


        tmpsoup = ""
        
        for line in self.jdtitles:
            if re.search(u"公司介绍",line.get_text()):
                tmpsoup = line.find_next("p","view-aboutUs")
                break
        
        if tmpsoup:
            self.result_inc["incIntro"] = tmpsoup.get_text(strip=True)


    def regular_inc_tag(self):

        tmpsoup = ""
        
        for line in self.jdtitles:
            if re.search(u"招聘公司",line.get_text()):
                tmpsoup = line.find_next("ul","view-ul")
                break
        
        if tmpsoup:
            res = {}
            tags = tmpsoup.find_all("li")
            for tag in tags:
                if re.search(u"公司名",tag.span.get_text()):
                    self.result_inc["incName"] = tag.get_text("|",strip=True).split("|")[-1]
                    if tag.find("a"):
                        self.result_inc["incUrl"] = tag.find("a").get("href","")
                elif re.search(u"所属行业",tag.span.get_text()):
                    res["incIndustry"] = tag.get_text("|",strip=True).split("|")[-1]
                elif re.search(u"公司性质",tag.span.get_text()):
                    res["incType"] = tag.get_text("|",strip=True).split("|")[-1]
                elif re.search(u"公司规模",tag.span.get_text()):
                    res["incScale"] = tag.get_text("|",strip=True).split("|")[-1]
                elif re.search(u"公司地址",tag.span.get_text()):
                    res["incLocation"] = tag.get_text("|",strip=True).split("|")[-1]

        self.result_inc.update(res)



    def regular_pubtime(self):
        """
        发布时间 & 截止时间
        """
        # 在基本信息 job_tag 中处理

        self.result["pubTime"] = ""



    def regular_jobname(self):
        """
        包括福利亮点
        """
        find_jobname = self.jdsoup.find("h1","postitonName")
        if find_jobname:
            jobname = find_jobname.find("span").get_text().strip()
            self.result_job["jobPosition"] = jobname
            find_welfare = find_jobname.find("div","labelList")
            if find_welfare:
                tags = [ tag.get_text() for tag in find_welfare.find_all("span") ]
                self.result_job["jobWelfare"] = "\n".join(tags)
                


    def regular_job_tag(self):

        tmpsoup = ""
        for line in self.jdtitles:
            if re.search(u"基本信息",line.get_text()):
                tmpsoup = line.find_next_siblings("ul","view-ul")
                break
        
        if tmpsoup:
            tags = [ tag for tmpul in tmpsoup for tag in tmpul.find_all("li") ]
            res = {}
            for tag in tags:
                if re.search(u"职位类",tag.get_text()):
                    res["jobCate"] = tag.get_text("|",strip=True).split("|")[-1]

                elif re.search(u"所属部门",tag.span.get_text()):
                    self.result_job["others"]["jobDepartment"] = tag.get_text("|",strip=True).split("|")[-1]

                elif re.search(u"工作地点",tag.span.get_text()):
                    res["jobWorkLoc"] = tag.get_text("|",strip=True).split("|")[-1]

                elif re.search(u"发布时间",tag.span.get_text()):
                    self.result["pubTime"] = tag.get_text("|",strip=True).split("|")[-1]

                elif re.search(u"截止时间",tag.span.get_text()):
                    self.result["endTime"] = tag.get_text("|",strip=True).split("|")[-1]

                elif re.search(u"汇报对象",tag.span.get_text()):
                    self.result_job["others"]["jobReport"] = tag.get_text("|",strip=True).split("|")[-1]

                elif re.search(u"下属人数",tag.span.get_text()):
                    self.result_job["others"]["jobSubSize"] = tag.get_text("|",strip=True).split("|")[-1]

                elif re.search(u"招聘人数",tag.span.get_text()):
                    res["jobNum"] = tag.get_text("|",strip=True).split("|")[-1]
        
        self.result_job.update(res)

    
    def regular_pay(self):
        
        tmpsoup = ""
        for line in self.jdtitles:
            if re.search(u"薪酬信息",line.get_text()):
                tmpsoup = line.find_next_sibling("ul")
                break

        if tmpsoup:
            res = tmpsoup.find("li").get_text(strip=True)
            self.result_job["jobSalary"] = res
   


    def regular_sex(self):
        find_sex = re.search(u"男|女|性别不限|不限男女",self.jdstr)
        if find_sex:
            self.result_job["gender"] = find_sex.group()



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
        res = "" 
        if self.demandsoup:
            find_demand = self.demandsoup.find("div","v-p-lable",text=re.compile(u"任职资格"))
            if find_demand:
                res = find_demand.find_next("div").get_text(strip=True)

        self.result_job['workDemand'] = res



    def regular_duty(self):
        res = ""
        if self.demandsoup:
            find_duty = self.demandsoup.find("div","v-p-lable",text=re.compile(u"岗位职责"))
            if find_duty:
                res = find_duty.find_next("div").get_text(strip=True)

        self.result_job['workDuty'] = res



    def regular_other(self):

        tmpsoup = ""
        for line in self.jdtitles:
            if re.search(u"其他要求",line.get_text()):
                tmpsoup = line.find_next_sibling("div","add-div800 clearfix")
                break
         
        if tmpsoup:
            tags = tmpsoup.find_all("li")
            tags.extend( tmpsoup.find_next_siblings("div","clearfix") )
            res = {}
            for tag in tags:
                if re.search(u"工作经验",tag.get_text()):
                    res["jobWorkAge"] = tag.span.get_text(strip=True)

                elif re.search(u"学历要求",tag.get_text()):
                    res["jobDiploma"] = tag.get_text("|",strip=True).split("|")[-1]
                
                elif re.search(u"年龄",tag.get_text()):
                    res["age"] = tag.get_text("|",strip=True).split("|")[-1]

                elif re.search(u"是否统招全日制",tag.get_text()):
                    self.result_job["others"]["isFullTime"] = tag.get_text(strip=True)
                
                elif re.search(u"海外经历",tag.get_text()):
                    self.result_job["others"]["overSea"] = tag.get_text("|",strip=True).split("|")[-1]

                elif re.search(u"专业要求",tag.get_text()):
                    res["jobMajorList"] = [tag.get_text("|",strip=True).split("|")[-1]]

                elif re.search(u"语言要求",tag.get_text()):
                    res["language"] = tag.get_text("|",strip=True).split("|")[-1]
                
                elif re.search(u"补充说明",tag.get_text()):
                    self.result_job["others"]["other"] = tag.get_text("|",strip=True).split("|")[-1]
       

        find_jobreport = self.jdsoup.find("h6",text=re.compile(u"汇报对象"))
        if find_jobreport:
            self.result_job["others"]["jobReportDetail"] = find_jobreport.find_next("div").get_text().strip()

        self.result_job.update(res)

        self.result_job["jobDesc"] = self.jdstr

        self.result["jdInc"] = self.result_inc
        self.result["jdJob"] = self.result_job
        self.result_job["others"] = self.result_job.pop("others")




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
        self.regular_pay()
        self.regular_duty()
        self.regular_demand()
        self.regular_other()
        
        return self.result


    def parser_detail(self,htmlContent=None,fname=None,url=None):
        """
        进一步简单的语义解析，卓聘一样
        """
        
        self.preprocess(htmlContent,fname,url)
        self.regular_incname()
        self.regular_inc_tag()
        self.regular_pubtime()
        self.regular_jobname()
        self.regular_job_tag()
        self.regular_sex()
        self.regular_pay()
        self.regular_skill()
        self.regular_cert()
        self.regular_duty()
        self.regular_demand()
        self.regular_other()
        
        return self.result




if __name__ == "__main__":
    import os,json 

    test = JdParserHighPin()
    path = './test_jds/highpin/'
    fnames = [ path+fname for fname in os.listdir(path) ]
    for fname in fnames:
        print '==='*20,fname
        htmlContent = codecs.open(fname,'rb','utf-8').read()
        result1 = test.parser_basic(htmlContent,fname=None)
        print json.dumps(result1,ensure_ascii=False,indent=4)

        print "detail"
        result2 = test.parser_detail(htmlContent)
        print json.dumps(result2,ensure_ascii=False,indent=4)

