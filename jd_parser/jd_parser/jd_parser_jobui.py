#!/usr/bin/env python
# coding=utf-8

import sys,re,codecs,jieba
from bs4 import BeautifulSoup
from urllib2 import urlopen
from collections import OrderedDict,Counter
from base import JdParserTop

reload(sys)
sys.setdefaultencoding('utf-8')


class JdParserJobUI(JdParserTop):
    """
    http://www.jobui.com/job/105454857/
    对结合html，对职友集 进行解析
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

        self.jdsoup = self.soup.find("div",{"class":"jk-box jk-matter j-job-detail"})
        
        find_comp = self.soup.find("div","aright")
        if find_comp and find_comp.find("span",text=re.compile(u"行业：")):
            self.compsoup = self.soup.find("div","aright").find("span",text=re.compile(u"行业：")).find_previous("ul")
        else:
            self.compsoup = ""

        jdstr = self.jdsoup.find("div","hasVist cfix sbox").get_text().strip()
        self.jdstr = self.CLEAN_TEXT.sub(" ",jdstr)

        self.linelist = [ line.strip() for line in self.SPLIT_LINE.split(self.jdstr) if len(line)>1]
    
        # 先存储下来，方便解析基本字段
        self.jdbasic_soup = self.jdsoup.find("ul","laver cfix").find_all("li")
   


    def regular_incname(self):
        incname = "None"
        if not self.compsoup and self.jdsoup.find_previous("div","sbox"):
            incname = self.jdsoup.find_previous("div","sbox").find("a","fs18 sbox f000 fwb block").get_text()
        if not self.compsoup:
            self.result_inc['incName'] = incname.strip()
            return 

        incname = self.compsoup.find_previous('h2').get_text()
        if re.search(u"概况",incname):
            incname = self.jdsoup.find_previous("div","sbox").find("a","fs18 sbox f000 fwb block").get_text()
        self.result_inc['incName'] = incname.strip()


    def regular_inc_tag(self):
        res = {"incUrl":"","incIntro":""}
        
        inc_tags = self.compsoup.find_all("span") if self.compsoup else []
        
        inc_tags2 = self.jdsoup.find_next("div","cfix jk-box jk-matter")
        if inc_tags2 and inc_tags2.find("dl","dlli"):
            inc_tags.extend(inc_tags2.find("dl","dlli").find_all("dt"))

        for tag in inc_tags:
            key = tag.get_text()
            if re.search(u"性质：",key):
                res["incType"] = tag.find_next_sibling("span").get_text().strip()
            elif re.search(u"行业：",key) and tag.find_next_sibling("span"):
                res['incIndustry'] = tag.find_next_sibling("span").get_text().strip()
            elif re.search(u"规模：",key) and tag.find_next_sibling("span"):
                res["incScale"] = tag.find_next_sibling("span").get_text().strip()

            elif re.search(u"地址：",key) and tag.find_next_sibling("dd"):
                res["incLocation"] = tag.find_next_sibling("dd").get_text().strip()[:-5]
            elif re.search(u"网站：",key) and tag.find_next("a"):
                res["incUrl"] = tag.find_next("a").get('href','None').strip()
        
        self.result_inc.update(res)




    def regular_pubtime(self):
        """
        发布时间 & 截止时间
        """
        
        tmpsoup = self.jdsoup.find("div","cfix").find_all("dt")
        if tmpsoup:
            for tag in tmpsoup:
                if re.search(u"发布时|截止日",tag.get_text()):
                    self.result["pubTime"] = tag.find_next("dd").get_text().strip()
                
                elif re.search(u"截止时间|截止日",tag.get_text()):
                    self.result["endTime"] = tag.find_next("dd").get_text().strip()

                elif re.search(u"来源网站",tag.get_text()):
                    self.result["jdFrom"] = tag.find_next("dd").get_text().strip()


    def regular_jobname(self):
        jobname = self.soup.find("body").find("div","head cfix").find("h1").get_text()
        self.result_job['jobPosition'] = re.sub("\s+","",jobname.strip().lower())



    def regular_job_tag(self):
        res = {"jobCate":"",'jobType':"全职","jobNum":""}
        
        for li in self.jdbasic_soup:
            key = li.span.get_text()
            if re.search(u"职位类型",key):
                res["jobType"] = li.get_text().strip().replace(key,"")
            elif re.search(u"招聘人数",key):
                res['jobNum'] = li.get_text().strip().replace(key,"")
            elif re.search(u"类别",key):
                res["jobCate"] = li.get_text().strip().replace(key,"")

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
        agestr=u"不限"
        for line in self.linelist:
            if re.search(u"\d+后",line):continue
            if self.AGE.search(line):
                findage = re.search(u"\d{2}?\s?[\-　－到至]?\s?\d{2}周?岁|(至少|不低于|不超过|不大于|大概|大约|不少于|大于)\d+周?岁|\d+周岁(以上|左右|上下)",line)
                if findage:
                    agestr = findage.group()

        self.result_job['age'] = agestr


    def regular_major(self):
        res = set()
        for line in self.linelist:
            for word in jieba.cut(line):
                word = word.lower()
                if word in self.majordic:
                    res.add(word)
            if res:
                break

        self.result_job["jobMajorList"] = list(res)



    def regular_degree(self):
        degree = ""
        for li in self.jdbasic_soup:
            key = li.span.get_text()
            if re.search(u"学历",key):
                degree = li.get_text().strip()
                break

        self.result_job['jobDiploma'] = re.sub(u"学历要求：|\s+","",degree)
        return degree


    
    def regular_degree_detail(self):
        res = self.regular_degree()

        if not res:
            res = []
            for line in self.linelist:
                for word in jieba.cut(line):
                    if word in self.degreedic:
                        res.append(word)

            self.result_job["jobDiploma"] = " | ".join(res)
        else:
            self.result_job['jobDiploma'] = re.sub(u"学历要求：|\s+","",res)



    def regular_exp(self):

        expstr = ""
        for li in self.jdbasic_soup:
            if re.search(u"工作经验",li.span.get_text()):
                expstr = li.get_text()
                break

        self.result_job['jobWorkAge'] = re.sub(u"工作经验：|\s+","",expstr)
    

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
        res = ""
        for li in self.jdbasic_soup:
            key = li.span.get_text()
            if re.search(u"工作地点",key):
                res = li.get_text().strip().replace(key,"")
                break
        
        self.result_job['jobWorkLoc'] = res



    def regular_pay(self):

        paystr = ""
        for li in self.jdbasic_soup:
            key = li.span.get_text()
            if re.search(u"薪资",key):
                paystr = li.get_text().strip().replace(key,"")
       
        self.result_job['jobSalary'] = paystr.replace(u"k","000")

    
    def regular_cert(self):
        res = []
        for line in self.linelist:
            findcert = self.CERT.search(line)
            if findcert and len(findcert.group())<6 and not re.search(u"保证",findcert.group()):
                res.append(findcert.group())
            else:
                findcert = re.search(u"有(.{2,5}证)",line)
                if findcert and not re.search(u"保证",findcert.group()):
                    res.append(findcert.group(1))
        res = re.sub(u"[通过或以上至少]","","|".join(res))
        self.result_job['certList'] = res.split("|")

    


    def regular_demand(self):
        jdstr = self.jdsoup.find("div","hasVist cfix sbox").get_text()
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

        jdstr = self.jdsoup.find("div","hasVist cfix sbox").get_text()
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
                
        self.result_job['jobWelfare'] = ""


    def regular_other(self):
        jdstr = self.jdsoup.find("div","hasVist cfix sbox").get_text()
        self.result_job["jobDesc"] = jdstr.strip()
        self.result["jdInc"] = self.result_inc.copy()
        self.result["jdJob"] = self.result_job.copy()
        self.result["jdFrom"] = self.result.get("jdFrom","jobui")
    
    
    def parser_basic(self,htmlContent=None,fname=None,url=None):
        self.preprocess(htmlContent,fname,url)
        self.regular_incname()
        self.regular_inc_tag()
        self.regular_pubtime()
        self.regular_jobname()
        self.regular_job_tag()
        self.regular_degree()
        self.regular_exp()
        self.regular_workplace()
        self.regular_pay()
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
        self.regular_degree_detail()
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
            print  k
            if isinstance(v,dict):
                for kk,vv in v.items():
                    print kk
                    print vv
            else:
                print v
            print '--'*20
                



if __name__ == "__main__":
    import os,json
    test = JdParserJobUI()
    path = '/home/jkmiao/Desktop/html/'
    fnames = [ path+fname for fname in os.listdir(path) if fname.endswith(".html") ][:20]
    for fname in fnames:
        print '=='*20,fname
        htmlContent = codecs.open(fname,'rb','utf-8').read()

        print 'detail'
        result2 = test.parser_detail(htmlContent)
        print json.dumps(result2,ensure_ascii=False,indent=4)
        print ''


