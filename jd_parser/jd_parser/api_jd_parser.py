#!/usr/bin/env python
# coding=utf-8


from jd_parser_lagou import JdParserLagou
from jd_parser_zhilian import JdParserZhiLian
from jd_parser_51job import JdParser51Job
from jd_parser_liepin import JdParserLiePin

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
    #   self.jd_parser_plain = JdParserPlain()


    def parser(self,htmlContent=None,fname=None,url=None,jdFrom=None):
        """
        根据jdFrom 参数选择合适的解析器进行解析

        """

        if not jdFrom:
            raise ValueError("jdFrom invalid")

        if re.search(u"lagou",jdFrom):
            result = self.jd_parser_lagou.parser(htmlContent,fname,url)
        elif re.search(u"51job",jdFrom):
            result = self.jd_parser_51job.parser(htmlContent,fname,url)
        elif re.search(u"zhilian",jdFrom):
            result = self.jd_parser_zhilian.parser(htmlContent,fname,url)
        elif re.search(u"liepin",jdFrom):
            result = self.jd_parser_liepin.parser(htmlContent)
        elif re.search(u"plain",jdFrom):
            result = self.jd_parser_plain.parser(jdstr=htmlContent)

        else:
            result = {"error":"jdFrom invalid!"}
        
        return result




    def output(self,result):
        for k,v in result.iteritems():
            print k
            if isinstance(v,list):
                print '[',','.join(result[k]),']'
            else:
                print result[k]
        print "-"*20




def cv_parser_http(htmlContent=None,jdFrom="zhilian",url="http://192.168.1.169:8088/jdstring"):
    """
    http 调用接口
    """

    result = requests.post(url,data={"htmlContent":htmlContent,"jdFrom":jdFrom})

    return result.content





if __name__=="__main__":
    test = JdParser()
    path = './test_jds/51job//'
    fnames = [ path+fname for fname in os.listdir(path)][:5]


    for i,fname in enumerate(fnames):
        print '%d th :'%(i+1),
        print '='*20,fname
        
        # 关键点，输入下载好的html源码，直接解析出结果
        # 输入文件名 test.parser(fname=file_name)
        # 输入url test.parser(url)
        html = codecs.open(fname,'rb','gb18030').read()
        result = test.parser(htmlContent=html,jdFrom=path)

#        print cv_parser_http(html,jdFrom=path)
        test.output(result)

        print ""
    print "url" 
    print test.parser(url="http://www.lagou.com/jobs/1385898.html",jdFrom="lagou")

