#!/usr/bin/env python
# coding=utf-8

import sys,re,codecs
from bs4 import BeautifulSoup
from urllib2 import urlopen
from collections import OrderedDict
from base import CvTopParser
import pdb
import os
reload(sys)
sys.setdefaultencoding('utf-8')


class CvParser51Job(CvTopParser):
    """
    对51job的简历进行解析
    """
    def __init__(self):


        CvTopParser.__init__(self)

        self.result = OrderedDict()
        self.PAY = re.compile(u"(\d+[\s\-])?\d+元")
        self.UPDATETIME = re.compile("更新日期[:：\s](\d+年\d+月\d+日)")
        self.ADDR = re.compile(u"居住地[：:\s](\S+)")
        self.JOB_START = re.compile(u"(.+)--",re.S)
        self.JOB_END = re.compile(u"--(.+)[:：]",re.S)
        self.JOB_DURATION = re.compile(u"\[(.+)\]")
        self.INC_SCALE = re.compile(u"[\(（](.+)人[\)、）]")
        self.INC_NAME = re.compile(u"[：:>](\S+?)[\(\[<【\r\n ]")
        self.JOB_DEPARTMENT = re.compile(u"部门[:\s：](\S+)",re.S)
        self.PROJ_NAME = re.compile(u"[:：](\S+)")
        


    def preprocess(self,htmlContent=None,fname=None,url=None):
        if url!=None:
            self.html= urlopen(url).read().decode('utf-8')
        elif htmlContent:
            self.html = htmlContent
        elif fname:
            self.html = codecs.open(fname,'rb','gb18030').read()
        else:
            raise Exception("input error")

        if re.search(u"已被(求职者)?删除|无法查看",self.html):
            raise Exception("error: input illegal cv ")

        self.soup = BeautifulSoup(self.html,"lxml")
        
        if self.soup.find("title") and re.search(u"简历ID",self.soup.find("title").get_text()):
            self.NoName = 1
            self.resume = self.soup.find('div',{"id":"divResume"})
            self.topsoup = self.resume.find("table").find("table")
            self.field_list = self.resume.find_all("td","cvtitle")
        else:
            self.NoName = 0
            print '---'*20,self.NoName
            self.resume = self.soup.find("body").find("table").find_next_sibling("table").find("table")
            self.topsoup = self.resume.find("table").find("table")
            self.field_list = self.resume.find_all("div","titleLineB")

        self.result.clear()
        self.result["privateInfo"] = {}
        


    def regular_basic(self):
        """
        解析基本信息
        """

        res = {}

        find_update_time = self.soup.find("div",{"id":"divHead"}).find("span",{"id":"lblResumeUpdateTime"}).get_text() if self.NoName else "None"
        res["updateTime"] = find_update_time.split(u"：")[-1].strip() if find_update_time else "None"
        
        if not self.NoName:
            res["name"] = self.topsoup.find("strong").get_text()
        base_info = self.topsoup.get_text()
        if re.search(u"最近工作",self.topsoup.find_next_sibling("table").get_text()):
            base_info2 = self.topsoup.find_next_sibling("table")
            if base_info2:
                items = base_info2.find_all("td")
                for item in items:
                    if not item.find_next_sibling("td"):continue
                    if re.search(u"公.?司",item.get_text()):
                        res["nowInc"] = item.find_next_sibling("td").get_text().strip()
                    elif re.search(u"行.?业",item.get_text()):
                        res["nowIndustry"] = item.find_next_sibling("td").get_text().strip()
                    elif re.search(u"职.?位",item.get_text()):
                        res["nowPosition"] = item.find_next_sibling("td").get_text().strip()

                    elif re.search(u"学.历",item.get_text()):
                        items2 = item.find_next("table").find_all("td")
                        cnt = 1
                        for item in items2:
                            if not item.find_next_sibling("td"):
                                cnt += 1
                                continue
                            if re.search(u"学.?历",item.get_text()):
                                res["nowDiploma"] = item.find_next_sibling("td").get_text().strip()
                            elif re.search(u"学.?校",item.get_text()):
                                res["recentSchName"] = item.find_next_sibling("td").get_text().strip()
                            elif re.search(u"专.?业",item.get_text()):
                                res["rescentMajorName"] = item.find_next_sibling("td").get_text().strip()
                            if cnt>3:break

        find_cv_id = self.CV_ID.search(base_info)
        res["cvId"] = find_cv_id.group(1).strip() if find_cv_id else "None"


        find_sex = self.SEX.search(base_info)
        res["gender"]= find_sex.group() if find_sex else "0"

        find_age =  self.AGE.search(base_info)
        res["age"] = find_age.group() if find_age else "0"
       
        find_dob = self.DOB.search(base_info)
        res["dob"] = find_dob.group(1) if find_dob else "None"

        find_exp = self.EXP.search(base_info)
        res["nowWorkAge"] = find_exp.group(1) if find_exp else "None"
        
        if "nowDiploma" not in res:
            find_degree = self.DEGREE.search(base_info)
            res["nowDiploma"] = find_degree.group() if find_degree else "None"

        find_marriage = self.MARRIAGE.search(base_info)
        res["marriage"] = find_marriage.group() if find_marriage else "None"
        

        find_politic = self.POLITIC.search(base_info)
        res["nowPolistatus"] = find_politic.group() if find_politic else u"群众"

        #　居住地和户口
        items = self.topsoup.find_all("td")
        tmpid = 0
        for item in items:
            if re.search(u"居住地",item.get_text()) and item.find_next_sibling("td"):
                res["nowAddress"] = item.find_next_sibling("td").get_text().strip()
                tmpid += 1
            elif re.search(u"户.{0,3}口",item.get_text()) and item.find_next_sibling("td"):
                res["nowHukou"] = item.find_next_sibling("td").get_text().strip()
                tmpid += 1
            if tmpid>1:break

        find_height = self.HEIGHT.search(base_info)
        res["height"] = find_height.group(1) if find_height else "None"

        find_oversea = self.OVER_SEA.search(base_info)
        res["overSea"] = "1" if find_oversea else "None"
        
        self.result['baseInfo'] =  res


    # 求职意向
    def regular_expect(self):

        res = {}

        soup = ""
        for field in self.field_list:
            if re.search(u"求职意向",field.get_text()):
                if self.NoName:
                    soup = field.find_next("table")
                else:
                    soup = field.find_previous("table")
                break

        if soup:
            rows = soup.find_all("tr") if self.NoName else soup.find_all("tr")[1:]
            for item in rows:
                if re.search(u"目标地.",item.find("td").get_text()):
                    res["expLocations"] = item.find("td").find_next().get_text()

                elif re.search(u"月薪|薪资|工资|薪酬",item.find("td").get_text()):
                    res["expSalary"] = self.CLEAN_TEXT.sub("",item.find("td").find_next().get_text())

                elif re.search(u"目前状况|求职状态",item.find("td").get_text()):
                    res["workStatus"] = item.find("td").find_next().get_text()

                elif re.search(u"工作性.",item.find("td").get_text()):
                    res["expJobTypes"] = item.find("td").find_next().get_text()

                elif re.search(u"期望.{0,4}行业",item.find("td").get_text()):
                    res["expIndustrys"] = item.find("td").find_next().get_text()

                elif re.search(u"目标职能|期望.{0,4}职[业位]",item.find("td").get_text()):
                    res["expPositions"] = item.find("td").find_next().get_text()

                elif re.search(u"到岗时间",item.find("td").get_text()):
                    res["dutyTime"] = item.find("td").find_next().get_text().strip()

                elif re.search(u"勿推荐|不要推荐",item.find("td").get_text()):
                    res["ignoreIncs"] = item.find("td").find_next().get_text().strip()

                elif re.search(u"目标职能|期望职能",item.find("td").get_text()):
                    res["expJobCates"] = item.find("td").find_next().get_text().strip()

        self.result['jobExp'] = res




    # 教育经历
    def regular_educate(self):

        soup = ""
        for field in self.field_list:
            if re.search(u"教育经历",field.get_text()):
                soup = field.find_next("table")
                break
        res = []
        if soup:
            rows = soup.find_all("tr")
            id = 1
            for item in rows:
                tokens =[ token.get_text().strip() for token in  item.find_all("td") if len(token.get_text())>1]
                tmp = {}
                if len(tokens)==4:
                    tmp["itemId"] = str(id)
                    tmp["eduStart"] = self.clean_edu_time(tokens[0].split("-")[0])
                    tmp["eduEnd"] = self.clean_edu_time(tokens[0].split("-")[-1])
                    tmp["schName"] = tokens[1]
                    tmp["majorName"] = tokens[2]
                    tmp["eduDiploma"] = tokens[3]
                    id += 1
                    res.append(tmp)

        if res:
            # 基本信息中的最高学历学校，专业
            self.result["baseInfo"]["recentSchName"] = res[0]["schName"]
            self.result["baseInfo"]["recentMajorName"] = res[0]["majorName"]
        self.result['eduList'] = res




    #　工作经历
    def regular_workexp(self):
        
        soup = ""
        for field in self.field_list:
            if re.search(u"工作经.",field.get_text()):
                soup = field.find_next("table")
                break

        res = []

        if soup:
            rows = soup.find_all("tr")
#            if self.NoName else soup.find_all("tr")[1:]
            id = 1
            tokens,tmp = [],[]
            for item in rows:
                if item.find("hr"):
                    tokens.append(tmp)
                    tmp = []
                    continue
                else:
                    tmp.append(item)
            if tmp:
                tokens.append(tmp)

            for token in tokens:
                tmp = {}
                if len(token)>3:
                    tmp["itemId"] = str(id)
                    job_title = token[0].find("td").get_text().strip()
                    tmp["jobStart"] = self.clean_edu_time(self.JOB_START.search(job_title).group(1)) if self.JOB_START.search(job_title) else job_title[:6]
                    tmp["jobEnd"] = self.clean_edu_time(self.JOB_END.search(job_title).group(1)) if self.JOB_END.search(job_title) else "None"
                    tmp["jobDuration"] = self.JOB_DURATION.search(job_title).group(1).strip() if self.JOB_DURATION.search(job_title) else "None"

                    tmp["incEmployee"] = self.INC_SCALE.search(job_title).group(1).strip() if self.INC_SCALE.search(job_title) else "None"           
                    
                    tmp["jobDesc"] = token[3].get_text().strip()
                        
                    if self.NoName:
                        tmp["incName"] = self.INC_NAME.search(job_title).group(1).strip() if self.INC_NAME.search(job_title) else "None"
                        if re.search(u"所属行业",token[1].get_text()):
                            tmp["incIndustrys"] =  token[1].find_all("td")[-1].get_text().strip()

                        jobTagItem = token[2].find_all("td")
                        if len(jobTagItem)==1:
                            tmp["jobPosition"] = jobTagItem[0].get_text().strip()
                        elif len(jobTagItem)==2:
                            tmp["jobPosition"] = jobTagItem[1].get_text().strip()
                            tmp["jobDepartment"] = jobTagItem[0].get_text().strip()
                        elif len(jobTagItem)==3:
                            tmp["jobPosition"] = jobTagItem[1].get_text().strip()
                            tmp["jobDepartment"] = jobTagItem[0].get_text().strip()
                            tmp["jobSalary"] = jobTagItem[2].get_text().strip()

                    else:
                        if token[0].find("td").find('b'):
                            tmp["incName"] = token[0].find("td").find("b").get_text().strip()

                        if re.search(u"职位名称",token[1].get_text()):
                            tmp["jobPosition"] = token[1].find("td").find("b").get_text().strip()
                            tmp["jobDepartment"] = self.JOB_DEPARTMENT.search(token[1].find('td').get_text()).group(1) if self.JOB_DEPARTMENT.search(token[1].find("td").get_text()) else "None"
                        
                        if re.search(u"行业",token[2].get_text()):
                            tmp["incIndustrys"] = token[2].find("td").get_text().strip()[3:]
                        


                    id += 1
                    res.append(tmp)
       
        self.result['jobList'] = res


    # 语言技能
    def regular_language(self):

        
        soup = ""
        for field in self.field_list:
            if re.search(u"语言.?能.?",field.get_text()):
                soup = field.find_next("table")
                break


        res = []
        id = 1
        if soup:
            if self.NoName==0 and soup.find("table"):
                soup = soup.find("table")

            rows = soup.find_all("tr") 
            for item in rows:
                tokens = [ i.get_text() for i in item.find_all("td") if i]
                if len(tokens)!=2:
                    tokens = re.split(u"[:：]",item.get_text(),maxsplit=1)
                if not len(tokens)==2:
                    tokens = re.split(u"[（\(]",item.get_text())
                if len(tokens)==2:
                    tmp = {}
                    tmp["itemId"] = str(id)
                    tmp["languageName"] = self.CLEAN_TEXT.sub("",tokens[0])
                    tmp["languageLevel"] =self.CLEAN_TEXT.sub("",tokens[1])
                    res.append(tmp)
                    id += 1

        self.result["languageList"] = res


    #　证书
    def regular_cert(self):
        

        soup =""
        for field in self.field_list:
            if field and re.search(u"证书",field.get_text()):
                soup = field.find_next("table")
                break

        res = []
        id = 1
        if soup:
            items = soup.find_all("tr") 
            for item in items:
                tokens = item.find_all("td")
                if len(tokens)<2:continue
                tmp = {}
                tmp["itemId"] = str(id)
                tmp["certTime"] = self.clean_edu_time(tokens[0].get_text())
                tmp["certName"] = tokens[1].get_text().strip()
                cert_str = tmp["certName"]
                find_level = self.CERT_LEVEL.search(cert_str)
                if find_level:
                    tmp["certLevel"] = find_level.group()
                    tmp["certName"] = re.sub(find_level.group(),"",tmp["certName"])
                else:
                    tmp["certLevel"] = "None"

                if tmp:
                    res.append(tmp)
                    id += 1

        self.result["certList"] = res
   
    
    # 技能
    def regular_skill(self):
        """
        技能模块
        """

        soup = ""
        for field in self.field_list:
            if re.search(u"技能",field.get_text()):
                soup = field.find_next("table")
                break

        res = []
        id = 1
        if soup:
            items = soup.find_all("tr") 
            for item in items:
                tokens = [token.get_text() for token in item.find_all("td")]
                if len(tokens)<2 or re.search(u"名称",tokens[0]):continue
                tmp = {}
                tmp["itemId"] = str(id)
                tmp["skillName"] = tokens[0].strip().lower()
                tmp["skillLevel"] = tokens[1].strip()

                if len(tokens)>2:
                    tmp["skillDuration"] = tokens[2].strip()
                else:
                    find_duration = re.search("\d+月|[半一二三四五六七八九十\d]年",item.get_text())
                    tmp["skillDuration"] = find_duration.group() if find_duration else "None"

                if tmp:
                    res.append(tmp)
                    id += 1


        self.result['skillList'] = res

     
    #　项目经验
    def regular_project(self):

        soup = ""
        for field in self.field_list:
            if re.search(u"项目经.",field.get_text()):
                soup = field.find_next("table")
                break

        res = []
        id = 1
        if soup:
            items = soup.find_all("tr") 

            tokens,tmpitem =[],[]
            for item in items:
                if item.find("hr"):
                    tokens.append(tmpitem)
                    tmpitem = []
                    continue
                else:
                    tmpitem.append(item)
            if tmpitem:
                tokens.append(tmpitem)

            for token in tokens:
                if len(token)<3:
                    continue

                # 解析第一行项目标题
                title_str = token[0].get_text()
                tmp = {}
                tmp["itemId"] = str(id)
                tmp["proStart"] = self.clean_edu_time(self.JOB_START.search(title_str).group(1)) if self.JOB_START.search(title_str) else "None" 
                tmp["proEnd"] = self.clean_edu_time(self.JOB_END.search(title_str).group(1)) if self.JOB_END.search(title_str) else "None" 
                tmp["proName"] =self.CLEAN_TEXT.sub("",self.PROJ_NAME.search(title_str).group(1)) if self.PROJ_NAME.search(title_str) else "None"
                
                #　解析剩余行标签
                field_list = [ item.find("td") for item in token[1:] ]
                for field in field_list:
                    field_str = field.get_text().strip()

                    find_duty = re.search(u"责任描述",field_str)
                    find_desc = re.search(u"项目描述",field_str)
                    find_soffwareEnv = re.search(u"开发工具",field_str)

                    if find_duty:
                        tmp["proDuty"] = field.find_next("td").get_text()
                    elif find_desc:
                        tmp["proDesc"] = field.find_next("td").get_text()
                    elif find_soffwareEnv:
                        tmp["softwareEnv"] = field.find_next("td").get_text()

                if tmp:
                    res.append(tmp)
                    id += 1

        self.result['proList'] = res




    def regular_train(self):

        soup = ""
        for field in self.field_list:
            if re.search(u"培训经.",field.get_text()):
                soup = field.find_next("table")
                break

        res = []
        id = 1
        if soup:
            items = soup.find_all("tr") 
            for item in items:
                tokens =[item.get_text() for item in item.find_all("td") if len(item.get_text())>1]
                if len(tokens)<3:continue
                tmp = {}
                tmp["itemId"] = str(id)
                tmp["trainStart"] = self.clean_edu_time(tokens[0].split(u'-')[0])
                tmp["trainEnd"] = self.clean_edu_time(tokens[0].split(u"-")[-1])
                tmp["trainAgency"] = tokens[1].strip()
                tmp["trainTitle"] = tokens[-1].strip()
                res.append(tmp)
                id += 1

        self.result["trainList"] = res

    
    def regular_private(self):
        """
        身份证号，联系电话等隐私信息
        """
        
        res = {}
        base_info = self.resume.find("table").find("table").get_text()
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
        
        other = ""
        for field in self.field_list:
            if re.search(u"其他|个人简介|自我介绍|亮点|兴趣爱好|著作|论文|作品",field.get_text()):
                other = field.find_next().get_text().strip()
                break
        
        self.result['baseInfo']["intro"] = other


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
    test = CvParser51Job()

    path = './data/cv_51job/'
    fnames = [ path+fname for fname in os.listdir(path) if not fname.find("name")>1][-20:-4]

    for i,fname in enumerate(fnames):
        print i+1,'='*20,fname
        htmlContent = codecs.open(fname,'rb','utf-8').read()
        test.parser(htmlContent = htmlContent)
        print(json.dumps(test.result,ensure_ascii=False,indent=4))
