#!/usr/bin/env python
# coding=utf-8

import sys

import re
import logging

# 要先安装这两个库
import ipin.rpc.etl.jd.analyze.JdAnalyzeService as jdService
from ipin.rpc.etl.jd.jd_type.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer


from jd_parser_lagou import JdParserLagou
from jd_parser_zhilian import JdParserZhiLian
from jd_parser_51job import JdParser51Job
from jd_parser_liepin import JdParserLiePin

reload(sys)
sys.setdefaultencoding('utf-8')
logging.basicConfig()

import simplejson as json


class JDHandler(object):

    def __init__(self):
        # 初始化四个网站的解析器
        self.jd_parser_lagou = JdParserLagou()
        self.jd_parser_zhilian = JdParserZhiLian()
        self.jd_parser_51job = JdParser51Job()
        self.jd_parser_liepin = JdParserLiePin()


    def analyzeHtml(self,htmlContent=None,jdFrom=None):
        """
        jd_html: 输入的html源码,
        jd_from:[lagou,51job,zhilian,liepin]中的一个
        """
        result = dict()
        result_inc = dict()
        result_job = dict()

        if re.search(u"lagou",jdFrom):
            result = self.jd_parser_lagou.parser(htmlContent)

        elif re.search(u"zhilian",jdFrom):
            result = self.jd_parser_zhilian.parser(htmlContent)

        elif re.search(u"51job",jdFrom):
            result = self.jd_parser_51job.parser(htmlContent)

        elif re.search(u"liepin",jdFrom):
            result = self.jd_parser_liepin.parser(htmlContent)
       
        print(json.dumps(result,ensure_ascii=False,indent=4))

        result_inc["incName"] = result["incName"]
        result_inc["incIndustry"] = result["incIndustry"]
        result_inc["incType"] = result["incType"]
        result_inc["incScale"] = result["incScale"]
        result_inc["incIntro"] = result["incIntro"]
        result_inc["incUrl"] = result["incUrl"]
        result_inc["incLocation"] = result["incLocation"]

        result_job["jobPosition"] = result["jobName"]
        result_job["gender"] = result["sex"]
        result_job["minAge"] = result["age"][0]
        result_job["maxAge"] = result["age"][1]
        result_job["jobDiploma"] = result["degree"]
        result_job["jobMajorList"] = result["major"]
        result_job["jobWorkAgeMin"] = result["exp"][0]
        result_job["jobWorkAgeMax"] = result["exp"][1]
        result_job["jobSalaryMin"] = result["pay"][0]
        result_job["jobSalaryMax"] = result["pay"][1]
        result_job["jobWorkLoc"] = result["workplace"]
        result_job["jobCate"] = result["jobCate"]
        result_job["jobType"] = result["jobType"]
        result_job["certList"] = result['cert']
        result_job["skillList"] = result["skill"]
        result_job["workDemand"] = result["demand"]
        result_job["workDuty"] =  result["duty"]
        result_job["jobWelfare"] = result["benefit"]
        
        result_job["jobDescription"] = result['duty']+"\n\n"+result["demand"]
        pubTime = result["pub_time"]
        result.clear()
        # jdId 和　jdUrl 需要处理时填充
        result["jdId"] = "None"
        result["jdUrl"] = "None"
        result["jdFrom"] = jdFrom
        result["jdInc"] = JdIncRaw(**result_inc)
        result["jdJob"] = JdJobRaw(**result_job)
        result["pubTime"] = pubTime

        result = JdRaw(**result)

        return result




if __name__=="__main__":
    handler = JDHandler()

    fname = './test_jds/zhilian/zhilian_jd_102.html'
    inputstr =  open(fname).read()
    res = handler.analyzeHtml(inputstr,jdFrom="zhilian")

    processor = jdService.Processor(handler)
    transport = TSocket.TServerSocket(port=9098)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor,transport,tfactory,pfactory)
    print 'Starting the thrift server at port 9098...'
    server.serve()
    print 'done'

