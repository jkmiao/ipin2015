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


class CvParserZhiLian(CvTopParser):
    """
    对智联的简历进行解析
    """
    def __init__(self):

        CvTopParser.__init__(self)

        self.PAY = re.compile(u"(\d+[\s\-])?\d+元")
        self.UPDATETIME = re.compile("更新日期[:：\s](\d+年\d+月\d+日)")
        self.ADDR = re.compile(u"现居住地[：:\s](\S+)")
        self.result = OrderedDict()


    def preprocess(self,htmlContent=None,fname=None,url=None):
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

        self.resume = self.soup.find('div',{"id":"resumeContentBody"})
        self.field_list = self.resume.find_all("div","resume-preview-all")

        self.content = self.resume.get_text().strip()
        self.result.clear()
        self.result["privateInfo"] = {}
        


    # 解析基本信息
    def regular_basic(self):
        res = OrderedDict()

        base_info = self.resume.find("div","summary-top").get_text()
        find_update_time = self.soup.find("strong",{"id":"resumeUpdateTime"})
        res["updateTime"] = find_update_time.get_text().strip() if find_update_time else "None"

        find_cv_id = self.soup.find("div","resume-left-tips").find("span","resume-left-tips-id")
        res["cvId"] = find_cv_id.get_text().strip()[3:] if find_cv_id else "None"


        find_sex = self.SEX.search(base_info)
        res["gender"]= find_sex.group() if find_sex else "0"

        find_age =  self.AGE.search(base_info)
        res["age"] = find_age.group() if find_age else "0"
       
        find_dob = self.DOB.search(base_info)
        res["dob"] = find_dob.group(1) if find_dob else "None"

        find_exp = self.EXP.search(base_info)
        res["nowWorkAge"] = find_exp.group(1) if find_exp else "None"

        find_degree = self.DEGREE.search(base_info)
        res["nowDiploma"] = find_degree.group() if find_degree else "None"

        find_marriage = self.MARRIAGE.search(base_info)
        res["marriage"] = find_marriage.group() if find_marriage else "None"

        find_addr = self.ADDR.search(base_info)
        res["nowAddress"] = find_addr.group(1) if find_addr else "None"

        find_politic = self.POLITIC.search(base_info)
        res["nowPolistatus"] = find_politic.group() if find_politic else u"群众"

        find_hukou = self.HUKOU.search(base_info)
        res["nowHukou"] = find_hukou.group(1) if find_hukou else "None"

        find_height = self.HEIGHT.search(base_info)
        res["height"] = find_height.group(1) if find_height else "None"

        find_oversea = self.OVER_SEA.search(base_info)
        res["overSea"] = "1" if find_oversea else "0"

        self.result['baseInfo'] =  res



    # 求职意向
    def regular_expect(self):

        res = OrderedDict()
        expsoup = ""
        for field in self.field_list:
            if re.search(u"求职意向",field.find("h3").get_text()):
                expsoup = field
                break

        if expsoup:
            rows = expsoup.find_all("tr")
            for item in rows:
                if re.search(u"期望工作地",item.find("td").get_text()):
                    res["expLocations"] = item.find("td").find_next().get_text()

                elif re.search(u"月薪|薪资|工资|薪酬",item.find("td").get_text()):
                    res["expSalary"] = item.find("td").find_next().get_text()

                elif re.search(u"目前状况",item.find("td").get_text()):
                    res["workStatus"] = item.find("td").find_next().get_text()

                elif re.search(u"期望工作性",item.find("td").get_text()):
                    res["expJobTypes"] = item.find("td").find_next().get_text()

                elif re.search(u"期望.{0,4}行业",item.find("td").get_text()):
                    res["expIndustrys"] = item.find("td").find_next().get_text()

                elif re.search(u"期望.{0,4}职[业位]",item.find("td").get_text()):
                    res["expPositions"] = item.find("td").find_next().get_text()

                elif re.search(u"到岗时间",item.find("td").get_text()):
                    res["dutyTime"] = item.find("td").find_next().get_text().strip()

                elif re.search(u"勿推荐|不要推荐",item.find("td").get_text()):
                    res["ignoreIncs"] = item.find("td").find_next().get_text().strip()

                elif re.search(u"期望职能",item.find("td").get_text()):
                    res["expJobCates"] = item.find("td").find_next().get_text().strip()

        self.result['jobExp'] = res




    # 教育经历
    def regular_educate(self):

        edusoup = ""
        for field in self.field_list:
            if re.search(u"教育经历",field.find("h3").get_text()):
                edusoup = field
                break
        res = []
        if edusoup:
            rows = edusoup.find("div","resume-preview-dl educationContent").get_text().split("\n")
            id = 1
            for item in rows:
                tokens = item.split()
                tmp = {}
                if len(tokens)==6:
                    tmp["itemId"] = str(id)
                    tmp["eduStart"] = self.clean_edu_time(tokens[0])
                    tmp["eduEnd"] = self.clean_edu_time(tokens[2])
                    tmp["schName"] = tokens[3]
                    tmp["majorName"] = tokens[4]
                    tmp["eduDiploma"] = tokens[5]
                    id += 1
                    res.append(tmp)

        if res:
            # 基本信息中的最高学历学校，专业
            self.result["baseInfo"]["recentSchName"] = res[0]["schName"]
            self.result["baseInfo"]["recentMajorName"] = res[0]["majorName"]
        self.result['eduList'] = res




    #　工作经历
    def regular_workexp(self):
        
        worksoup = ""
        for field in self.field_list:
            if re.search(u"工作经历",field.find("h3").get_text()):
                worksoup = field
                break

        res = []
        if worksoup:
            rows = worksoup.find_all("h2")
            id = 1
            for item in rows:
                tokens = item.get_text().split()
                tmp = {}
                if len(tokens)==5:
                    tmp["itemId"] = str(id)
                    tmp["jobStart"] = self.clean_edu_time(tokens[0])
                    tmp["jobEnd"] = self.clean_edu_time(tokens[2].strip())
                    tmp["incName"] = tokens[3].strip()
                    tmp["jobDuration"] = tokens[4].strip()[1:-1]

                    jobTagItem = item.find_next("h5").get_text().split('|')
                    if len(jobTagItem)==1:
                        tmp["jobPosition"] = jobTagItem[0].strip()
                    elif len(jobTagItem)==2:
                        tmp["jobPosition"] = jobTagItem[0].strip()
                        tmp["jobDepartment"] = jobTagItem[1].strip()
                    elif len(jobTagItem)==3:
                        tmp["jobPosition"] = jobTagItem[0].strip()
                        tmp["jobDepartment"] = jobTagItem[1].strip()
                        tmp["jobSalary"] = jobTagItem[2].strip()
                    
                    incTagItem = item.find_next("div","resume-preview-dl").get_text().split("|")
                    if len(incTagItem)==1:
                        tmp["incIndustrys"] = incTagItem[0].strip()

                    elif len(incTagItem)==2:
                        tmp["incIndustrys"] = incTagItem[0].strip()
                        tmp["incType"] = incTagItem[1].strip()

                    elif len(incTagItem)==3:
                        tmp["incIndustrys"] = incTagItem[0].strip()
                        tmp["incType"] = incTagItem[1].strip()[5:]
                        tmp["incEmployee"] = incTagItem[2].strip()[3:]

                    tmp["jobDesc"] = item.find_next("table").get_text().strip()[5:]
                    id += 1

                res.append(tmp)
       
        self.result['jobList'] = res


    # 语言技能
    def regular_language(self):

        
        langsoup = ""
        for field in self.field_list:
            if re.search(u"语言.?能.?",field.find("h3").get_text()):
                langsoup = field
                break

        res = []
        id = 1
        if langsoup:
            rows = langsoup.find_all("div","resume-preview-dl")
            for item in rows:
                tokens = re.split(u"[:：]",item.get_text())
                if len(tokens)==2:
                    tmp = {}
                    tmp["itemId"] = str(id)
                    tmp["languageName"] = tokens[0].strip()
                    tmp["languageLevel"] = tokens[1].strip()
                    res.append(tmp)
                    id += 1

        self.result["languageList"] = res


    #　证书
    def regular_cert(self):
        

        certsoup =""
        for field in self.field_list:
            if re.search(u"证书",field.find("h3").get_text()):
                certsoup = field
                break

        res = []
        id = 1
        if certsoup:
            items = certsoup.find_all("h2")
            for item in items:
                tokens = item.get_text().split()
                if len(tokens)<2:continue
                tmp={}
                tmp["itemId"] = str(id)
                tmp["certTime"] = tokens[0].strip()
                tmp["certName"] = tokens[1].strip()
                
                if item.find_next_sibling("div","resume-preview-dl"):
                    cert_str = item.find_next_sibling("div").find_all("td")[-1].get_text()
                else:
                    cert_str = tokens[1]

                find_level = self.CERT_LEVEL.search(cert_str)
                tmp["certLevel"] = find_level.group() if find_level else "None"

                res.append(tmp)
                id += 1

        self.result["certList"] = res
   
    
    # 技能
    def regular_skill(self):
        """
        技能模块
        """

        skillsoup = ""
        for field in self.field_list:
            if re.search(u"技能",field.find("h3").get_text()):
                skillsoup = field
                break
        res = []
        id =1
        if skillsoup:
            items = skillsoup.find_all("div","resume-preview-dl")
            for item in items:
                tokens = [token for token in re.split(u"[:：| ]",item.get_text()) if len(token.strip())>1]
                if len(tokens)<2:continue
                tmp = {}
                tmp["itemId"] = str(id)
                tmp["skillName"] = tokens[0].strip()
                tmp["skillLevel"] = tokens[1].strip()
                find_duration = re.search("\d+月|[半一二三四五六七八九十\d]年",item.get_text())
                tmp["skillDuration"] = find_duration.group() if find_duration else "None"
                res.append(tmp)

        self.result['skillList'] = res

     
    #　项目经验
    def regular_project(self):

        prosoup = ""
        for field in self.field_list:
            if re.search(u"项目经历",field.find("h3").get_text()):
                prosoup = field
                break
        
        res = []
        id = 1
        if prosoup:
            items = prosoup.find_all("h2")
            for item in items:
                tokens = [token for token in item.get_text().split() if len(token.strip())>1]
                if len(tokens)<3:continue
                tmp = {}
                tmp["itemId"] = str(id)
                tmp["proStart"] = tokens[0].strip()
                tmp["proEnd"] = tokens[1].strip()
                tmp["proName"] = tokens[2].strip()

                field_list = item.find_next("table").find_all("td")
                for field in field_list:
                    find_duty = re.search(u"责任描述",field.get_text())
                    find_desc = re.search(u"项目描述",field.get_text())
                    if find_duty:
                        tmp["proDuty"] = field.find_next("td").get_text()
                    elif find_desc:
                        tmp["proDesc"] = field.find_next("td").get_text()
                res.append(tmp)
                id += 1

        self.result['proList'] = res

    def regular_train(self):

        trainsoup = ""
        for field in self.field_list:
            if re.search(u"培训经历",field.find("h3").get_text()):
                trainsoup = field
                break

        res = []
        id = 1
        if trainsoup:
            items = trainsoup.find_all("h2")
            for item in items:
                tokens = [ token for token in item.get_text().split() if len(token.strip())>1 ]
                if len(tokens)<3:continue

                tmp = {}
                tmp["itemId"] = str(id)
                tmp["trainStart"] = tokens[0]
                tmp["trainEnd"] = tokens[1]
                tmp["trainTitle"] = tokens[2]

                field_list = item.find_next("table").find_all("td")
                for field in field_list:
                    find_agency = re.search(u"培训机构：",field.get_text())
                    find_location = re.search(u"培训地点",field.get_text())
                    find_desc = re.search(u"培训描述",field.get_text())

                    if find_agency:
                        tmp["trainAgency"] = field.find_next_sibling("td").get_text() if field.find_next_sibling("td") else "None"

                    elif find_location:
                        tmp["trainLoc"] = field.find_next_sibling("td").get_text() if field.find_next_sibling("td") else "None"

                    elif find_desc:
                        tmp["trainDesc"] = field.find_next_sibling("td").get_text() if field.find_next_sibling("td") else "None"

                res.append(tmp)
                id += 1

        self.result["trainList"] = res

    
    def regular_private(self):
        """
        身份证号，联系电话等隐私信息
        """
        
        base_info = self.resume.find("div","summary-top").get_text()
        find_keyword = self.resume.find("div","resume-preview-list")
        res = {}
        if find_keyword:
            keywords = [ word.strip() for word in find_keyword.find_next("strong").get_text().split() if len(word.strip())>1 and not re.search("[（\(]")]
            res["keywords"] = keywords

        find_phone = self.PHONE.search(base_info)
        find_email = self.EMAIL.search(base_info)
        find_qq = self.QQ.search(base_info)
        find_idNum = self.IDNUM.search(base_info)
        
        res["phoneNumber"] = find_phone.group(1) if find_phone else "None"
        res["email"] = find_email.group(1) if find_email else "None"
        res["qq"] = find_qq.group(1) if find_qq else "None"
        res["idNumber"] = find_idNum.group(1) if find_idNum else "None"

        self.result["privateInfo"] = res



    def regular_other(self):
        
        other = ""
        for field in self.field_list:
            if re.search(u"其他|个人简介|自我介绍|亮点|兴趣爱好|著作|论文|作品",field.find("h3").get_text()):
                other = field.find_next("div").get_text().strip()
                break
     
        self.result['baseInfo']["intro"] = other

        if self.result["baseInfo"]["cvId"] != "None":
            self.result["cvId"] = self.result["baseInfo"]["cvId"]


    def parser(self,htmlContent=None,fname=None,url=None):
        self.preprocess(htmlContent,fname,url)
        self.regular_basic()
        self.regular_private()
        self.regular_expect()
        self.regular_educate()
        self.regular_workexp()
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
                    res += '%1s: %s\n' %( kk,vv )
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
    """
    测试
    """
    test = CvParserZhiLian()
    path = './data/cv_zhilian/'
    fnames = [ path+fname for fname in os.listdir(path)][:10]

    for i,fname in enumerate(fnames):
        try:
            print i+1,'='*20,fname
            htmlContent = codecs.open(fname,'rb','utf-8').read()
            result = test.parser(htmlContent)
            output = test.output()
            print(json.dumps(result,ensure_ascii=False,indent=4))
            json.dump(result,open("output_cv_zhilian.json",'wb'))
#            print output
        except Exception,e:
            print e
            continue




