#!/usr/bin/env python
# coding=utf-8

import sys,re,codecs,jieba
from bs4 import BeautifulSoup
from urllib2 import urlopen
from collections import OrderedDict,Counter
from base import JdParserTop
import threading
reload(sys)
sys.setdefaultencoding('utf-8')


class JdParserZhiLian(JdParserTop):
    """
    对lagou Jd 结合html 进行解析
    """
    def __init__(self):
        JdParserTop.__init__(self)
        self.result = OrderedDict()


    def preprocess(self,htmlContent,fname=None,url=None):
        self.result.clear()
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

        self.soup = BeautifulSoup(self.html)

        self.jdsoup = self.soup.find("div","terminalpage-left")
        self.compsoup = self.soup.find("div","company-box")
        jdstr = self.jdsoup.find("div","tab-inner-cont").get_text().strip()
        self.jdstr = self.CLEAN_TEXT.sub(" ",jdstr)

        self.linelist = [ line.strip() for line in self.SPLIT_LINE.split(self.jdstr) if len(line)>1]
    
        # 针对智联额外增加的，方便解析基本字段
        self.jdtop_soup = self.soup.find("div","fixed-inner-box").find("div","inner-left fl")
        self.jdbasic_soup = self.jdsoup.find("ul","terminal-ul clearfix").find_all("li")
   


    def regular_incname(self):
        incname = self.compsoup.find('p',"company-name-t").get_text()
        self.result['incName'] = incname.strip()


    def regular_inc_tag(self):
        res = {"incUrl":"","incIntro":""}
        inc_tags = self.compsoup.find("ul").find_all("li")
        for tag in inc_tags:
            key = tag.find("span").get_text()
            if re.search(u"规模",key):
                res["incScale"] = tag.find("strong").get_text().strip()
            elif re.search(u"性质",key):
                res["incType"] = tag.find("strong").get_text().strip()
            elif re.search(u"行业",key):
                res['incIndustry'] = tag.find("strong").get_text().strip()
            elif re.search(u"主页",key):
                res["incUrl"] = tag.find("strong").get_text().strip()
            elif re.search(u"地址",key):
                res["incLocation"] = re.sub(u"查看公司地图|[\s　]","",tag.find("strong").get_text().strip())

        find_inc_intro = self.soup.find("div",{"class":"tab-inner-cont","style":"display:none;"})
        if re.search(u"公司介绍",self.html) and find_inc_intro:
            res["incIntro"] = find_inc_intro.get_text().strip()

        if len(res["incUrl"])<3 and res["incIntro"]:
            find_url = self.INC_URL.search(res["incIntro"])
            if find_url:
                res["incUrl"] = re.search(u"[\d\w\.:/_\-]+",find_url.group()).group()
        self.result.update(res)




    def regular_pubtime(self):
        """
        发布时间 & 截止时间
        """
        pub_time = self.jdbasic_soup[2].strong.get_text()
        self.result["pub_time"] = pub_time
        self.result["end_time"] = ""


    def regular_jobname(self):
        jobname = self.jdtop_soup.find('h1').get_text()
        self.result['jobName'] = self.CLEAN_JOBNAME.sub("",jobname.strip().lower())
       # self.result['jobName'] = self.clean_jobname(jobname.strip()) 更好，但比较慢


    def regular_job_tag(self):
        res = {"jobCate":"",'jobType':"全职","jobNum":""}
        
        for li in self.jdbasic_soup:
            if re.search(u"工作性质",li.span.get_text()):
                res["jobType"] = li.strong.get_text()
            elif re.search(u"招聘人数",li.span.get_text()):
                res['jobNum'] = li.strong.get_text()
            elif re.search(u"类别",li.span.get_text()):
                res["jobCate"] = li.strong.get_text()

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
                findage = re.search(u"\d{2}?\s?[\-　－到至]?\s?\d{2}周?岁|(至少|不低于|不超过|不大于|大概|大约|不少于|大于)\d+周?岁|\d+周岁(以上|左右|上下)",line)
                if findage:
                    agestr = findage.group()
                    age = re.findall("\d+",agestr)
                    if len(age)>1:
                        res[0],res[-1] = age[0],age[-1]
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
                if word in self.majordic:
                    res.append(word)
            if res:
                break

        self.result["major"] = list(set(res))



    def regular_degree(self):
        degree = ""
        if re.search(u"学历",self.jdsoup.find("ul").get_text()):
            degree = self.jdbasic_soup[5].strong.get_text()
        for w in jieba.cut(degree):
            if w in self.degreedic:
                degree = w
                break
        self.result['degree'] = degree



    def regular_exp(self):
        res = [0,100]
        for li in self.jdbasic_soup:
            if re.search(u"工作经验",li.span.get_text()):
                expstr = li.strong.get_text()
                break

        exp = re.findall("\d+",expstr)

        if len(exp)==1:
            if re.search(u"以上|大于|至少|超过|不少于",expstr):
                res[0]= exp[0]
        elif len(exp)>1:
            res[0],res[1] = exp[0],exp[1]

        self.result['exp'] = map(str,res)
    

    def regular_skill(self):
        res = []
        for line in self.linelist:
            for word in jieba.cut(line):
                word = word.lower()
                if word in self.skilldic:
                    res.append(word)
        res =[w[0] for w in Counter(res).most_common(5)]
        self.result["skill"] = res



    def regular_workplace(self):
        res = ""
        if re.search(u"工作地点",self.jdsoup.find("ul").get_text()):
            res = self.jdbasic_soup[1].strong.get_text()
        
        self.result['workplace'] = res



    def regular_pay(self):
        res = [0,0]
        if re.search(u"职位月薪",self.jdsoup.find("ul").get_text()):
            paystr = self.jdbasic_soup[0].strong.get_text()
            pay = map(lambda x: re.sub("[kK]","000",x),re.findall("\d+[kK]?",paystr))
            if len(pay)==1:
                res[0] = pay[0]
            elif len(pay)>1:
                res[0],res[1] = pay[0],pay[-1]
        self.result['pay'] = map(str,res)

    
    def regular_cert(self):
        res = []
        for line in self.linelist:
            findcert = self.CERT.search(line)
            if findcert:
                res.append(findcert.group())
            else:
                findcert = re.search(u"有(.+资格证)",line)
                if findcert:
                    res.append(findcert.group())
        res = re.sub(u"[通过或以上至少]","","|".join(res))
        self.result['cert'] = res.split("|")

    


    def regular_demand(self):
        jdstr = self.jdsoup.find("div","tab-inner-cont").get_text()
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
        self.result['demand'] = '\n'.join(res)

    def regular_duty(self):

        jdstr = self.jdsoup.find("div","tab-inner-cont").get_text()
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
        self.result['duty'] = '\n'.join(res)

    def regular_benefit(self):
        jdstr = self.jdsoup.find("div","tab-inner-cont").get_text()
        res,linelist = [],[]
        
        job_tags = self.jdtop_soup.find("div","welfare-tab-box")
        if job_tags:
            job_tags = job_tags.find_all("span")
            for tag in job_tags:
                res.append(tag.get_text())

        pos = list(self.START_BENEFIT.finditer(jdstr))
        if not res and len(pos)>0:
            linelist = [ re.sub("[\s　]+"," ",line) for line in self.SPLIT_LINE.split(jdstr[pos[-1].span()[1]:]) if line>3]

            linelist = filter(lambda x:len(x)>2,linelist) 
            for i in range(len(linelist)):
                line = linelist[i]
                if len(line)<2:
                    continue
                if re.match(u"\d[、.\s ]|[（\(【][a-z\d][\.、\s ]|[\u25cf\uff0d]",line) or self.clf.predict(line)=="benefit":
                    res.append(self.CLEAN_LINE.sub("",line))
                elif i<len(linelist)-1 and self.clf.predict(linelist[i+1])=='benefit':
                    res.append(self.CLEAN_LINE.sub("",line))
                else:
                    break

            res = [ str(i)+". "+line for i,line in enumerate(res,1) ]
                
        self.result['benefit'] = '\n'.join(res)


    def regular_other(self):
        jdstr = self.jdsoup.find("div","tab-inner-cont").get_text()
        linelist = [ self.CLEAN_LINE(line) for line in self.SPLIT_LINE.split(jdstr) if len(line.strip())>5]
        res = []
        for line in linelist:
            if self.clf.predict(line)=='other':
                res.append(line)
                
        self.result['other'] = '\n'.join(res)
    
    
    def multi_process_parser(self,htmlContent=None,fname=None,url=None):

        self.preprocess(htmlContent,fname,url)
        thread_list = []
        thread_list.append(threading.Thread(target=self.regular_incname))
        thread_list.append(threading.Thread(target=self.regular_inc_tag))
        thread_list.append(threading.Thread(target=self.regular_pubtime))
        thread_list.append(threading.Thread(target=self.regular_job_tag))
        thread_list.append(threading.Thread(target=self.regular_jobname))
        thread_list.append(threading.Thread(target=self.regular_sex))
        thread_list.append(threading.Thread(target=self.regular_age))
        thread_list.append(threading.Thread(target=self.regular_major))
        thread_list.append(threading.Thread(target=self.regular_degree))
        thread_list.append(threading.Thread(target=self.regular_exp))
        thread_list.append(threading.Thread(target=self.regular_skill))
        thread_list.append(threading.Thread(target=self.regular_demand))
        thread_list.append(threading.Thread(target=self.regular_duty))
        thread_list.append(threading.Thread(target=self.regular_benefit))

        for t in thread_list:
            t.start()

        for t in thread_list:
            t.join()
        return self.result

    def parser(self,htmlContent=None,fname=None,url=None):
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

        return self.result

    def ouput(self):
        for line in self.linelist:
            print line

        for k,v in self.result.iteritems():
            print  k
            print v


if __name__ == "__main__":
    test = JdParserZhiLian()
    htmlContent = codecs.open('./test_jds/zhilian/zhilian_jd_102.html','rb','utf-8').read()
    test.parser(htmlContent,fname=None,url=None)
    test.multi_process_parser(htmlContent, fname=None, url=None)
    test.ouput()

