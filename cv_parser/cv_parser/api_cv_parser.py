#!/usr/bin/env python
# coding=utf-8

from cv_parser_58 import CvParser58
from cv_parser_51job import CvParser51Job
from cv_parser_zhilian import CvParserZhiLian

import simplejson as json
import requests

import re,os,sys
import codecs

reload(sys)
sys.setdefaultencoding('utf-8')


class CvParser:
    """
    lagou,智联和51job的html解析接口

    """

    def __init__(self):
        """
        声明３个cv解析器

        """
        self.cv_parser_58 = CvParser58()
        self.cv_parser_51job = CvParser51Job()
        self.cv_parser_zhilian = CvParserZhiLian()


    def parser(self,htmlContent=None,fname=None,url=None,cvFrom="lagou"):
        """
        根据jd_from 参数选择合适的解析器进行解析

        """
        result = {}
        if re.search(u"51job",cvFrom):
            result = self.cv_parser_51job.parser(htmlContent,fname,url)

        elif re.search(u"58",cvFrom):
            result = self.cv_parser_58.parser(htmlContent,fname,url)

        elif re.search(u"zhilian",cvFrom):
            result = self.cv_parser_zhilian.parser(htmlContent,fname,url)

        return result
    
    
def cv_parser_http(htmlContent=None,cvFrom="zhilian",url="http://192.168.1.91:8087/string"):
    """
    http api 接口
    """
    result = requests.post(url,data={"htmlContent":htmlContent,"cvFrom":cvFrom})

    return result.content



    

if __name__=="__main__":
    test = CvParser()
    print test.parser(url="http://jianli.m.58.com/resume/88735086993677/",cvFrom="58tongcheng")

    path = "./data/cv_zhilian/"
    fnames = [ path+fname for fname in os.listdir(path) if fname.endswith(".html")][:1]
    for i,fname in enumerate(fnames,1):
        print i,'='*20,fname
        
        # 关键点，输入下载好的html源码，直接解析出结果
        # 输入文件名 test.parser(fname=file_name)
        # 输入url test.parser(url)
        html = codecs.open(fname,'rb','utf-8').read()
        result = test.parser(htmlContent=html,cvFrom=path)
        print(result)
        print ""
   
    # http　接口直接调用示范
    htmlContent = codecs.open("./data/cv_zhilian/JM001946527R90250000000.html",'rb','utf-8').read()
    print cv_parser_http(htmlContent,cvFrom="zhilian")

