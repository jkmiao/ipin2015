#!/usr/bin/env python
# coding=utf-8

import sys,re,codecs
from bs4 import BeautifulSoup
from urllib2 import urlopen
from collections import OrderedDict
from base import CvTopParser
import os
reload(sys)
sys.setdefaultencoding('utf-8')


class CvParser58(CvTopParser):
    """
    对５８同城的简历进行解析
    """
    def __init__(self):

        CvTopParser.__init__(self)

        self.EDU_ENDTIME = re.compile(u"\d+-(\d+\.\d+)")

        self.result = OrderedDict()

    def preprocess(self,htmlContent=None,fname='./data/100.html',url=None):

        if url!=None:
            self.html= urlopen(url).read().decode('utf-8')
        elif htmlContent:
            self.html = htmlContent
        elif fname:
            self.html = codecs.open(fname,'rb','utf-8').read()
        else:
            raise Exception("input error")

        if re.search(u"已被(求职者)?删除|无法查看",self.html):
            raise Exception("error: input illegal cv ")

        self.soup = BeautifulSoup(self.html,"lxml")

        soup = BeautifulSoup(self.html)
        self.resume = soup.find('div','resume')
        self.field_list = self.resume.find_all("div","field")[1:]
        self.result.clear()
        self.result["privateInfo"]= {}

    
    
    def regular_basic(self):
        
        basicsoup = ""
        for field in self.field_list:
            if re.search(u"基本资料",field.find("h2","field-title").get_text()):
                basicsoup = field
                break
        
        res = OrderedDict()
        res["updateTime"] = self.resume.find("span",{"class":"last-modified"}).get_text()
        

        if basicsoup and basicsoup.find("ul","contact-list"):
            basic_list = self.resume.find("ul","contact-list").find_all('li')
            if len(basic_list)>7:
                self.result["privateInfo"]["userName"] = basic_list[0].get_text().strip()
                res['gender'] = basic_list[2].get_text().strip()
                res['age'] = basic_list[4].get_text().strip()
                res['nowWorkAge'] = basic_list[6].get_text().strip()
                res['nowDiploma'] = basic_list[8].get_text().strip()
        
        basic_str = basicsoup.get_text()

        find_marriage =  self.MARRIAGE.search(basic_str)
        res["marriage"] = find_marriage.group() if find_marriage else "None"

        find_height = self.HEIGHT.search(basic_str)
        res["height"] = find_height.group(1) if find_height else "None"

        find_oversea = self.OVER_SEA.search(basic_str)
        res["overSea"] = "1" if find_oversea else "None"
        

        self.result['baseInfo'] = res
        


    def regular_expect(self):

        expsoup = ""
        for field in self.field_list:
            if re.search(u"求职意向",field.find("h2","field-title").get_text()):
                expsoup = field
                break

        res = OrderedDict()
         
        if expsoup and expsoup.find("dl"):
            expect_list = expsoup.find_all('dd')
            res['expSalary'] = expect_list[0].get_text()
            res["expLocations"] = expect_list[1].get_text()
            res["expPositions"] = expect_list[2].get_text()

        self.result['jobExp'] = res




    def regular_educate(self):

        edusoup = ""
        for field in self.field_list:
            if re.search(u"教育经历",field.find("h2","field-title").get_text()):
                edusoup = field
                break

        res = []
        if edusoup and edusoup.find("dl"):
            items = [ item.find("p").get_text() for item in  edusoup.find_all("dl") ]
            id = 1
            for item in items:
                tokens = item.strip().split()
                tmp = {}
                if len(tokens) == 3:
                    tmp["itemId"] = str(id)
                    tmp["eduStart"] = tokens[0].split("-",1)[0]
                    tmp["eduEnd"] = self.EDU_ENDTIME.search(tokens[0]).group(1) if self.EDU_ENDTIME.search(tokens[0]) else "None"
                    tmp["schName"] = tokens[1]
                    tmp["majorName"] = tokens[2]
                    res.append(tmp)
                    id += 1

        self.result['eduList'] = res

        
    def regular_experience(self):
        
        worksoup = ""
        for field in self.field_list:
            if re.search(u"工作经验",field.find("h2","field-title").get_text()):
                worksoup = field
                break

        res = []
        if worksoup:
            items = worksoup.find_all("div","employed")
            id = 1
            for item in items:
                tmp = {}
                
                tmp["itemId"] = str(id)
                tmp["jobPosition"] = item.find("dd").get_text().strip()

                tokens = item.find_all("dl")[1:]
                for token in tokens:
                    if re.search(u"任职职位",token.find("dt").get_text()):
                        tmp['incName'] = token.find('dd').get_text().strip()

                    elif re.search(u"薪资",token.find("dt").get_text()):
                        tmp["jobSalary"] = token.find("dd").get_text()

                    elif re.search(u"在职时",token.find("dt").get_text()):
                        tmp["jobDuration"] = token.find("dd").get_text()
                        tmp["jobStart"],tmp["jobEnd"] = tmp["jobDuration"].split(u"-")

                    elif re.search(u"职责",token.find("dt").get_text()):
                        tmp["jobDesc"] = token.find("dd").get_text()
                res.append(tmp)
                id += 1

        self.result['jobList'] = res 



    def regular_language(self):

        langsoup = ""
        for field in self.field_list:
            if re.search(u"语言能力",field.find("h2","field-title").get_text()):
                langsoup = field
                break
        
        res = []

        if langsoup:
            items = langsoup.find_all("dl")
            id = 1
            for item in items:
                tmp = {}
                tmp["itemId"] = str(id)
                tmp["languageName"] = item.find("dt").get_text().strip()[:-1]
                tmp["languageLevel"] = item.find("dd").get_text().strip()
                find_level = self.CERT_LEVEL.search(tmp["languageLevel"])
                if find_level:
                    tmp["languageLevel"] = find_level.group()
                id += 1
                res.append(tmp)

        self.result["languageList"] = res





    def regular_cert(self):

        certsoup = ""
        for field in self.field_list:
            if re.search(u"语言能力",field.find("h2","field-title").get_text()):
                certsoup = field
                break
        
        res = []

        if certsoup:
            items = [ item.find("p") for item in  certsoup.find_all("dl") if item.find("p")]
            id = 1
            for cert in items:
                tmp = {}
                tmp["itemId"] = str(id)
                tmp['certName'] = cert.find("span").get_text().strip()
                tmp['certtime'] = re.search(u'<p>(.+)<span',str(cert)).group(1) if re.search(u"<p>(.+)<span",str(cert)) else "None"
                find_level = self.CERT_LEVEL.search(tmp["certName"])
                if find_level:
                    tmp["certLevel"] = find_level.group()
                id += 1
                res.append(tmp)
        self.result["certList"] = res
   
    

    def regular_skill(self):

        soup = ""
        for field in self.field_list:
            if re.search(u"专业技能",field.find("h2","field-title").get_text()):
                soup = field
                break

        res = []
        if soup:
            items = soup.find_all("dl")
            id = 1
            for item in items:
                tmp = {}
                tmp["itemId"] = str(id)
                tmp["skillName"] = item.find("dt").get_text()[:-1].strip().lower()
                tmp["skillLevel"],tmp["skillDuration"] = item.find("dd").get_text().split("|",1)
                res.append(tmp)
                id += 1

        self.result['skillList'] = res

     

    def regular_project(self):

        soup = ""
        for field in self.field_list:
            if re.search(u"项目经",field.find("h2","field-title").get_text()):
                soup = field
                break

        res = []
        if soup:
            items = soup.find_all("div","project")
            id = 1
            for item in items:
                tmp = {}
                tmp["itemId"] = str(id)
                tmp["proName"] = item.find("dd").find("strong").get_text().strip()

                tokens = item.find_all("dl")[1:]
                for token in tokens:
                    if not token.find("dt"):continue
                    if re.search(u"项目时间",token.find("dt").get_text()):
                        tmp["proStart"],tmp["proEnd"] = token.find("dd").get_text().split("-",1)

                    elif re.search(u"项目简介",token.find("dt").get_text()):
                        tmp["proDesc"] = token.find("dd").get_text().strip()

                    elif re.search(u"职责",token.find("dt").get_text()):
                        tmp["proDuty"] = token.find("dd").get_text().strip()

                res.append(tmp)
                id += 1

        self.result['proList'] = res



    def regular_train(self):

        soup = ""
        for field in self.field_list:
            if re.search(u"培训经历",field.find("h2","field-title").get_text()):
                soup = field
                break

        res = []
        if soup:
            items = soup.find_all("div","project")
            id = 1
            for item in items:
                tmp = {}
                tmp["itemId"] = str(id)
                tmp["trainName"] = item.find("dd").find("strong").get_text().strip()

                tokens = item.find_all("dl")[1:]
                for token in tokens:
                    if not token.find("dt"):continue
                    if re.search(u"时间",token.find("dt").get_text()):
                        tmp["trainStart"],tmp["proEnd"] = token.find("dd").get_text().split("-",1)

                    elif re.search(u"简介",token.find("dt").get_text()):
                        tmp["trainDesc"] = token.find("dd").get_text().strip()

                    elif re.search(u"机构",token.find("dt").get_text()):
                        tmp["trainAgency"] = token.find("dd").get_text().strip()

                res.append(tmp)
                id += 1

        self.result['trainList'] = res




    def regular_private(self):

        res = {}

        for field in self.field_list:
            if re.search(u"基本资料",field.find("h2","field-title").get_text()):
                soup = field
                break

        if soup:
            base_info = soup.get_text()
            find_phone = self.PHONE.search(base_info)
            find_email = self.EMAIL.search(base_info)
            find_qq = self.QQ.search(base_info)
            find_idNum = self.IDNUM.search(base_info)
            
            res["phoneNumber"] = find_phone.group() if find_phone else "None"
            res["email"] = find_email.group() if find_email else "None"
            res["qq"] = find_qq.group(1) if find_qq else "None"
            res["idNumber"] = find_idNum.group(1) if find_idNum else "None"

        self.result["privateInfo"] = res

    

    def regular_other(self):

        soup = ""
        for field in self.field_list:
            if re.search(u"我的亮点",field.find("h2","field-title").get_text()):
                soup = field
                break

        
        if soup and soup.find("p"):
            other = soup.find("p").get_text().strip()
            self.result['baseInfo']["intro"] = other
    



    def parser(self,htmlContent=None,fname=None,url=None):
        self.preprocess(htmlContent,fname,url)
        self.regular_basic()
        self.regular_expect()
        self.regular_educate()
        self.regular_experience()
        self.regular_skill()
        self.regular_cert()
        self.regular_language()
        self.regular_project()
        self.regular_train()
        self.regular_other()
        return self.result


    
    def output(self):
        res = "\n"
        for k in self.result:
            res += k+":"+"\n"
            if isinstance(self.result[k],dict):
                for kk,vv in self.result[k].iteritems():
                    res += '%10s: %s\n' %( kk,vv )
            elif isinstance(self.result[k],list):
                for i,exp in enumerate(self.result[k]):
                    res+= "%12s\n" % (str(i+1))
                    if isinstance(exp,dict):
                        for kk,vv in exp.iteritems():
                            res += "%22s: %s\n" % (kk,vv)
                    elif isinstance(exp,tuple):
                        for kk in exp:
                            res += '%22s \n'% (kk)
                    res += " "*10+'---'*10+'\n'
            else:
                res += " "*10+"%s\n" % (self.result[k])
        return res




import simplejson as json

if __name__ == "__main__":
    test = CvParser58()
    path = "./data/cv_58/"
    fnames = [ os.path.join(path,fname) for fname in os.listdir(path)][:10]

    for i,fname in enumerate(fnames,1):
        print i,'=='*10,fname
        htmlContent = codecs.open(fname,'rb','utf-8').read()
        result = test.parser(htmlContent)
        print(json.dumps(result,ensure_ascii=False,indent=4))

    result = test.parser(url="http://jianli.58.com/resume/88352411957514/")
    print(json.dumps(result,ensure_ascii=False,indent=4))
