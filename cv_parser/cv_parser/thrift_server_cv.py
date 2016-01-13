#!/usr/bin/env python
# coding=utf-8

import sys

import re
import logging

# 要先安装这两个库

import ipin.rpc.etl.cv.simple_parse.CvSimpleParseService as cvService
from ipin.rpc.etl.cv.cv_type.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from cv_parser_zhilian import CvParserZhiLian
from cv_parser_51job import CvParser51Job
from cv_parser_58 import CvParser58

reload(sys)
sys.setdefaultencoding('utf-8')
logging.basicConfig()


class CvHandler(object):

    def __init__(self):
        # 初始化3个网站的解析器

        self.cv_parser_zhilian = CvParserZhiLian()
        self.cv_parser_51job = CvParser51Job()
        self.cv_parser_58 = CvParser58()


    def parseHtml(self,htmlContent=None,cvFrom=None):
        """
        cv_html: 输入的html源码,
        cv_from:[58,51job,zhilian]中的一个
        """
        result = dict()

        if re.search(u"zhilian",cvFrom):
            result = self.cv_parser_zhilian.parser(htmlContent)

        elif re.search(u"51job",cvFrom):
            result = self.cv_parser_51job.parser(htmlContent)

        elif re.search(u"58",cvFrom):
            result = self.cv_parser_58.parser(htmlContent)
        

        # cvId 和　cvUrl ,cvFrom 根据情况需要处理时填充

        result["baseInfo"] = CvBaseInfoRaw(**result["baseInfo"])
        result["privateInfo"] = CvPrivateInfoRaw(**result["privateInfo"])
        result["jobExp"] = CvJobExpRaw(**result["jobExp"])
        result["eduList"] =[CvEduItemRaw(**x) for x in result["eduList"]]
        result["jobList"] =[CvJobItemRaw(**x) for x in result["jobList"]]
        result["proList"] =[CvProItemRaw(**x) for x in result["proList"]]
        result["certList"] =[CvCertItemRaw(**x) for x in result["certList"]]
        result["trainList"] =[CvTrainItemRaw(**x) for x in result["trainList"]]
        result["languageList"] = [CvLanguageItemRaw(**x) for x in result["languageList"]]
        result["skillList"] = [ CvSkillItemRaw(**x) for x in result["skillList"]]

        result = CvRaw(**result)

        return result


if __name__=="__main__":
    handler = CvHandler()

    fname = './data/cv_51job/10000215.html'
    inputstr =  open(fname).read()
    res = handler.parseHtml(inputstr,cvFrom="51job")
    processor = cvService.Processor(handler)
    transport = TSocket.TServerSocket(port=9097)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor,transport,tfactory,pfactory)
    print 'Starting the thrift server at port 9097...'
    server.serve()
    print 'done'
