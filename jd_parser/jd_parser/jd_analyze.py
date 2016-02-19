#!/usr/bin/env python
# coding=utf-8


from jd_parser_lagou import JdParserLagou
from jd_parser_zhilian import JdParserZhiLian
from jd_parser_51job import JdParser51Job
from jd_parser_liepin import JdParserLiePin
from jd_parser_jobui import JdParserJobUI
from collections import OrderedDict
import xlwt

import codecs
import requests
import re,os,sys

reload(sys)
sys.setdefaultencoding('utf-8')


class JdParser(object):
    """
    lagou,智联和51job的html解析接口

    """

    def __init__(self):
        """
        声明4个html－jd解析器和一个简单文本解析器

        """
        self.jd_parser_lagou = JdParserLagou()
        self.jd_parser_51job = JdParser51Job()
        self.jd_parser_zhilian = JdParserZhiLian()
        self.jd_parser_liepin = JdParserLiePin()
        self.jd_parser_jobui = JdParserJobUI()
    #   self.jd_parser_plain = JdParserPlain()


    def parser(self,htmlContent=None,fname=None,url=None,jdFrom=None):
        """
        jd_html: 输入的html源码,
        jd_from:[lagou,51job,zhilian,liepin]中的一个
        """

        if not jdFrom:
            raise ValueError("jdFrom invalid")

        p = None
        if re.search(u"lagou",jdFrom):
            p = self.jd_parser_lagou
        elif re.search(u"zhilian",jdFrom):
            p = self.jd_parser_zhilian
        elif re.search(u"51job",jdFrom):
            p = self.jd_parser_51job
        elif re.search(u"liepin",jdFrom):
            p = self.jd_parser_liepin
        elif re.search(u"jobui",jdFrom):
            p = self.jd_parser_jobui

        else:
            raise NameError("jdFrom invalid")

        try:
            result = p.parser_detail(htmlContent)
        except Exception as e:
            raise NameError(e.message)
            pass
        return result



    def normal_key(self,result):
        
        tmpItem = OrderedDict()
        
        for k,v in result.iteritems():
            if isinstance(v,dict):
                for kk,vv in v.items():
                    if isinstance(vv,dict):
                        for kkk,vvv in vv.items():
                            tmpItem[kkk] = str(vvv)
                    elif isinstance(vv,str):
                        tmpItem[kk] = str(vv)
                    elif isinstance(vv,list):
                        tmpItem[kk] = ','.join(vv)
                    elif isinstance(vv,str) or isinstance(vv,unicode):
                        tmpItem[kk] = str(vv)
                    else:
                        print kk
                        print type(kk)
            else:
                tmpItem[k] = str(v)

        return tmpItem



JOB_CATE = re.compile(u"运营|销售|产品|数据|开发|财务|测试|会计|业务|设计师|程序员|市场|商务|情报|法务|营销|策划|采购|行政|政府|客户|拓展|风险|人事|运维|软件|安全|用户|系统|工程师|招聘")

def jobName2jobCate(fname):

    if re.search(u"hr",fname.lower()):
        return u"HR"
    elif JOB_CATE.search(fname):
        return JOB_CATE.search(fname).group()
    else:
        return "OTHER"



def data2xls(data,fname="./test_jds/jd_jobui_output.xls"):
    wk = xlwt.Workbook()

    group_data = {}
    for jd in data:
        group_data.setdefault(jd["incName"],[]).append(jd)

    for name in group_data:
        ws = wk.add_sheet(name.decode('utf-8'))
        
        for col,jd in enumerate(data[0]):
            ws.write(0,col,jd)

        for i,result in enumerate(group_data[name],1):
            for j,key in enumerate(result):
                ws.write(i,j,result[key].decode('utf-8'))
    wk.save(fname)


def analyze_data(fname=None):
    import pandas as pd
    df1 = pd.read_excel(fname)
    df1["jobCate"] = map(lambda x:jobName2jobCate(x),df1["jobPosition"])
    table1 = df1.pivot_table(values="incType",index=["jobPosition","pubTime"],columns=["jobCate"],aggfunc="count")
    table1.to_excel("./test_jds/q1.xls")





def cv_parser_http(htmlContent=None,jdFrom="zhilian",url="http://192.168.1.169:8088/jdstring"):
    """
    http 调用接口
    """

    result = requests.post(url,data={"htmlContent":htmlContent,"jdFrom":jdFrom})

    return result.content


cnt = 1
def parser_single(fname):
    global cnt
    print fname,cnt
    htmlContent = codecs.open(fname,'rb','utf-8').read()
    result = test.parser(htmlContent,jdFrom="jobui")
    res = test.normal_key(result)
    res["jobCate"] = jobName2jobCate(res["jobPosition"].decode("utf-8"))
    res["file_name"] = fname.rsplit('/',1)[-1]
    cnt += 1
    return res


if __name__=="__main__":
    import multiprocessing ,time
    
    test = JdParser()

    path = '/home/jkmiao/Desktop/html/'
    fnames = [ path+fname for fname in os.listdir(path)]
    start = time.clock()
    pool = multiprocessing.Pool(8)
    data = pool.map(parser_single,fnames)
    data2xls(data,fname="./test_jds/jd_jobui_yy_new.xls")
    
    print 'done',cnt,len(data)
    print 'time used',time.clock()-start
