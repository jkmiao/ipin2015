#!/usr/bin/env python
# coding=utf-8

from jd_parser_lagou import JdParserLagou
from jd_parser_zhilian import JdParserZhiLian
from jd_parser_51job import JdParser51Job
from jd_parser_liepin import JdParserLiePin
from jd_parser_jobui import JdParserJobUI
from jd_parser_58tc import JdParser58tc
from jd_parser_highpin import JdParserHighPin

import requests
import re,os,sys,codecs
import simplejson as json

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
        self.jd_parser_58tc = JdParser58tc()
        self.jd_parser_highpin = JdParserHighPin()


    def parser(self,htmlContent=None,fname=None,url=None,jdFrom=None,detail=True):
        """
        :htmlContent 输入的html源码,
        :jd_from [lagou,51job,zhilian,liepin]中的一个
        :return 基本解析结果，仅仅做提取

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
        elif re.search(u"58tc",jdFrom):
            p = self.jd_parser_58tc
        elif re.search(u"highpin",jdFrom):
            p = self.jd_parser_highpin
        else:
            raise NameError("jdFrom invalid")

        try:
            if detail==True:
                result = p.parser_detail(htmlContent=htmlContent,url=url)  # 默认为详尽解析
            else:
                result = p.parser_basic(htmlContent=htmlContent,url=url)  # 更少字段但准确率较高的解析结果
        

        except Exception as e:
            raise NameError(e.message)
        
        return result


def jd_parser_http(htmlContent=None,jdFrom="zhilian",url="http://192.168.1.169:8088/jdstring"):
    """
    http 调用接口
    """

    result = requests.post(url,data={"htmlContent":htmlContent,"jdFrom":jdFrom})

    return result.content




if __name__=="__main__":
    test = JdParser()
    path = './test_jds/highpin/'

    fnames = [ path+fname for fname in os.listdir(path)]
    fnames.sort()
    
    for i,fname in enumerate(fnames):
        print '%d th :'%(i+1),
        print '='*20,fname

        # 关键点，输入下载好的html源码，直接解析出结果
        # 输入文件名 test.parser(fname=file_name)
        # 输入url test.parser(url)
        html = codecs.open(fname,'rb','utf-8').read()
#        result = test.parser(htmlContent=html,jdFrom=path,detail=False)
#        print json.dumps(result,ensure_ascii=False,indent=4)
        
        print 'detail'
        result = test.parser(htmlContent=html,jdFrom=path,detail=True)
        print json.dumps(result,ensure_ascii=False,indent=4)
