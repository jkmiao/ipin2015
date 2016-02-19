#!/usr/bin/env python
# coding=utf-8

import sys,re,codecs,jieba
from bs4 import BeautifulSoup
from urllib2 import urlopen
from collections import OrderedDict
from base import JdParserTop
reload(sys)
sys.setdefaultencoding('utf-8')


class JdParser51Job(JdParserTop):
    """
    对51job Jd 结合html 进行解析,分新旧两种情况判断并解析
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
        self.result["jdFrom"] = "51job"

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

        self.find_new_comp =  self.soup.find("div","tHeader tHjob") # 判断是否为新版本
        if not self.find_new_comp:
            self.jdsoup = self.soup.find("div","tCompany_introduction")
            self.compsoup = self.soup.find("div","tBorderTop_box job_page_company")
            self.lineDl = self.jdsoup.find("div","tCompany_basic_job").find_all("dl","lineDl") # 为了方便取出表格基本信息
            self.jdstr = self.jdsoup.find("div","tCompany_text").get_text().strip()
        
        else:
            self.compsoup = self.find_new_comp.find("div","cn")
            self.jdsoup = self.soup.find("div","tCompany_main")
            self.basicsoup = self.jdsoup.find("div","jtag inbox")
            self.lineDl = self.basicsoup.find("div","t1").find_all("span","sp4")
            self.lineDl2 = self.basicsoup.find("div","t1").find_all("span","sp2")  # 语言要求，专业要求
            self.jdstr = self.basicsoup.find_next("div","bmsg job_msg inbox").get_text().strip()

        self.jdstr = self.CLEAN_TEXT.sub(" ",self.jdstr)
        self.linelist = [ line.strip() for line in self.SPLIT_LINE.split(self.jdstr) if len(line.strip())>3]
    
    
    def regular_incname(self):
        incname=""
        if not self.find_new_comp and self.compsoup:
            incname = self.compsoup.find('h2').get_text()
        else:
            incname =  self.compsoup.find("p","cname").get_text() 
        self.result_inc['incName'] = incname.strip()


    def regular_inc_tag(self):
        res = {"incUrl":"","incIntro":"","incType":"","incLocation":"","incIndustry":"","incScale":""}
        if not self.compsoup:
            self.result.update(res)
            return 
        
        if self.find_new_comp:
            if self.compsoup.find("p","msg ltype"):
                res["incType"],res["incScale"],res["incIndustry"] =re.sub("\s+","",self.compsoup.find("p","msg ltype").get_text()).split("|")[:3]

            find_inc_intro = self.compsoup.find_next("div","tmsg inbox")
            if find_inc_intro:
                res["incIntro"] = find_inc_intro.get_text().strip()
                find_inc_url = self.compsoup.find("p","cname").find("a")
                if find_inc_url:
                    res["incUrl"] =  self.compsoup.find("p","cname").find("a").get("href","None") 
            find_inc_location = self.compsoup.find("span","lname")
            if find_inc_location:
                res["incLocation"] = find_inc_location.get_text().strip()
            
        else:
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
                res["incIntro"] = self.soup.find("div","tCompany_text_gsjs").get_text().strip().strip()

                incUrl = self.INC_URL.search(res["incIntro"])
                if not res["incUrl"] and incUrl:
                    res["incUrl"] = re.search("[\w\d\./_:\-]+",incUrl.group()).group()

        self.result_inc.update(res)
        


    def regular_pubtime(self):
        """
        发布时间 & 截止时间
        """
        
        pubTime =""
        if not self.find_new_comp:
            pubTime = self.jdsoup.find("div","tCompany_basic_job").dd.get_text().strip()
        self.result["pubTime"] = pubTime



    def regular_jobname(self):
        jobname = u""
        if self.find_new_comp:
            jobname = self.compsoup.find("h1").get_text().strip()
            find_job_type = re.search(u"实习|兼职|全职",jobname)
            if find_job_type:
                self.result_job["jobType"] = find_job_type.group()
        else:
            jobname = self.jdsoup.find("li","tCompany_job_name").find('h1').get_text()

        self.result_job["jobPosition"] = re.sub("\s+","",jobname.strip().lower())


    def regular_job_tag(self):
        res = OrderedDict()
        res["jobType"] = u"全职"
        
        if self.find_new_comp:
            for line in self.lineDl:
                if re.search(u"经验",line.get_text()):
                    res["jobWorkAge"] = line.get_text().strip()
                elif self.DEGREE.search(line.get_text()):
                    res["jobDiploma"] = line.get_text().strip()
                elif re.search(u"招聘|人",line.get_text()):
                    res["jobNum"] = line.get_text()
                elif re.search(u"发布",line.get_text()):
                    self.result["pubTime"] = line.get_text().strip()
                else:
                    print 'jobTag',line.get_text()
            find_job_cate = self.basicsoup.find_next("div","bmsg job_msg inbox").find("span","label",text=re.compile(u"职能类别"))
            if find_job_cate:
                tags = [tag.get_text() for tag in find_job_cate.find_next_siblings("span")]
                res["jobCate"] = ' | '.join(tags)

        else:

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
        self.result_job.update(res)


    def regular_sex(self):
        """
        不限
        男
        女
        """
        res = u"不限"
        for line in self.linelist:
                if re.search(u"性别不限|男女不限",line):
                    res = u"不限"
                elif re.search(u"男",line):
                    res = u"男"
                elif re.search(u"女",line):
                    res = u"女"
                break

        self.result_job["gender"] = str(res)


    def regular_age(self):
        """
        (minage,maxage)
        """ 
        agestr = u"不限"
        for line in self.linelist:
            if re.search(u"\d+后",line):continue
            if self.AGE.search(line):
                findage = re.search(u"\d{2}?\s?[\-－　到至\s]?\d{2}周?岁|(至少|不低于|不超过|不大于|大概|大约|不少于|大于)\d+周?岁|\d+周岁(以上|左右|以下)|年龄.{2,9}",line)
                if findage:
                    agestr = findage.group()
        self.result_job["age"] = agestr


    def regular_major(self):
        res = []
        if self.find_new_comp:
            for line in self.lineDl2:
                if line.find("em","i6"):
                    res = line.get_text().strip().split()

        self.result_job["jobMajorList"] = res


    def regular_major_detail(self):
        res = []
        if self.find_new_comp:
            for line in self.lineDl2:
                if line.find("em","i6"):
                    res = line.get_text().strip().split()
        if not res:
            for line in self.linelist:
                for word in jieba.cut(line):
                    word = word.strip().lower()
                    if word in self.majordic:
                        res.append(word)

        self.result_job["jobMajorList"] = list(set(res))


    def regular_degree(self):
        res = ""
        if not self.find_new_comp:
            line = self.lineDl[1] 
            for tag in line.find_all("dt"):
                if re.search(u"学历要求",tag.get_text()):
                    res = tag.findNext("dd").get_text()
                    self.result_job['jobDiploma'] = res
                    break
    



    def regular_language(self):

        if self.find_new_comp:
            for line in self.lineDl2:
                if re.search(u"好|语言",line.get_text()):
                    res = line.get_text().strip()
                    self.result_job["jobLanguage"] = res
                    break




    def regular_exp(self):
        expstr =""
        if not self.find_new_comp:
            for line in self.lineDl:
                if re.search(u"工作年限",line.dt.get_text()):
                    expstr = line.dd.get_text().strip()
                    self.result_job["jobWorkAge"] = expstr
                    break


    def regular_skill(self):
        res = {}
        for line in self.linelist:
            for word in jieba.cut(line):
                word = word.lower()
                if word in self.skilldic:
                    res.setdefault(word,1)
                    res[word] += 1

        sorted_res = sorted(res.items(),key = lambda d:d[1],reverse=True)

        res =[w[0] for w in sorted_res[:5] ]
        self.result_job["skillList"] = res



    def regular_workplace(self):
        res = ""
        
        if self.find_new_comp:
            find_workplace = self.jdsoup.find("span","label",text=re.compile(u"上班地址："))
            
            if find_workplace:
                res = find_workplace.find_previous("p","fp").get_text().strip()
                res = res[res.find(u"：")+1:]   # 去掉上班地址这几个字

        else: # 旧版本

            for line in self.lineDl:
                for tag in line.find_all("dt"):
                    if re.search(u"工作地点",tag.get_text()):
                        res = tag.findNext("dd").get_text()
                        break

        self.result_job['jobWorkLoc'] = res



    def regular_pay(self):
        """
        薪酬工资
        """

        paystr = ""
        if self.find_new_comp: #新版本
            find_pay = self.compsoup.find("p","cname").find_previous("strong")
            if find_pay:
                paystr = find_pay.get_text().strip()

        else:
            for line in self.lineDl:
                for tag in line.find_all("dt"):
                    if re.search(u"薪资范围",tag.get_text()):
                        paystr = tag.findNext("dd").get_text()
                        break
        self.result_job["jobSalary"] = paystr

    
    
    def regular_cert(self):
        """
        证书要求
        """
        res = []
        for line in self.linelist:
            findcert = self.CERT.search(line)
            if findcert and not re.search(u"保证",findcert.group()):
                res.append(findcert.group())
            else:
                findcert = re.search(u"有(.+资格证)",line)
                if findcert and not re.search(u"保证",findcert.group()):
                    res.append(findcert.group(1))
        res = re.sub(u"[通过或以上至少]","","|".join(res))
        self.result_job['certList'] = res.split("|")


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
        self.result_job["workDemand"] = '\n'.join(res)

    
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
        self.result_job["workDuty"] = '\n'.join(res)




    def regular_benefit(self):
        """
        福利制度
        """

        res = []
        
        if self.find_new_comp:
            find_benefit = self.basicsoup.find("div","t2") 
            if not find_benefit:
                find_benefit = self.basicsoup.find("p","t2")
            if find_benefit:
                for tag in find_benefit.find_all("span"):
                    res.append(tag.get_text().strip())
        else:
            for line in self.lineDl:
                if re.search(u"薪酬福利",line.find("dt").get_text()):
                    res.append(line.find("dd").get_text().strip())

        self.result_job["jobWelfare"] = '\n'.join(set(list(res)))



    def regular_other(self):
        """
        关键词，具体上班地址等信息
        """

        self.result_job["jobDesc"] = self.jdstr

        
        res = {}
        if self.find_new_comp:
            find_key_words = self.basicsoup.find_next("div","bmsg job_msg inbox").find("span","label",text=re.compile(u"关键字"))
            if find_key_words:
                tags = [tag.get_text() for tag in find_key_words.find_next_siblings("span")]
                res["keyWords"] = ' | '.join(tags)
            
            find_workp_detail = self.basicsoup.find_next("span","label",text=re.compile(u"上班地址"))
            if find_workp_detail:
                res["workPlaceDetail"] = re.sub("\s","",find_workp_detail.find_parent("p").get_text())[5:]


        self.result_job["others"] = res
        
        self.result["jdInc"] = self.result_inc
        self.result["jdJob"] = self.result_job 



    
    def parser_basic(self,htmlContent="",fname=None,url=None):
        """
        基本解析，简单抽取信息
        """
        self.preprocess(htmlContent,fname,url)
        self.regular_incname()
        self.regular_inc_tag()
        self.regular_pubtime()
        self.regular_jobname()
        self.regular_job_tag()
        self.regular_pay()
        self.regular_degree()
        self.regular_major()
        self.regular_exp()
        self.regular_language()
        self.regular_workplace()
        self.regular_benefit()
        self.regular_other()

        return self.result

    
    def parser_detail(self,htmlContent="",fname=None,url=None):
        """
        进一步简单语义解析
        """
        self.preprocess(htmlContent,fname,url)
        self.regular_exp()
        self.regular_incname()
        self.regular_inc_tag()
        self.regular_pubtime()
        self.regular_jobname()
        self.regular_job_tag()
        self.regular_pay()
        self.regular_degree()

        self.regular_sex()
        self.regular_age()
        self.regular_major_detail()
        self.regular_skill()
        self.regular_cert()

        self.regular_exp()
        self.regular_language()
        self.regular_workplace()
        self.regular_benefit()
        self.regular_other()

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
    import os,json
    test = JdParser51Job()

    path = './test_jds/51job/'
    fnames = [ path+file for file in os.listdir(path)][:10]

    for fname in fnames:
        print "=="*20,fname
        htmlContent = codecs.open(fname,'rb','gb18030').read()

        result1 = test.parser_basic(htmlContent,fname=None,url=None)
        print json.dumps(result1,ensure_ascii=False,indent=4)

        print 'detail'
        result2 = test.parser_detail(htmlContent,fname=None,url=None)
        print json.dumps(result2,ensure_ascii=False,indent=4)
