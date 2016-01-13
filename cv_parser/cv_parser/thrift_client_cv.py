#!/usr/bin/env python
# coding=utf-8


import ipin.rpc.etl.cv.simple_parse.CvSimpleParseService as cvService
from ipin.rpc.etl.cv.cv_type.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import codecs

import logging

logging.basicConfig()

import sys
reload(sys)

sys.setdefaultencoding("utf-8")


def getClient(addr='192.168.1.91',port=9097):
    print 'conneting server %s at port %d' %(addr,port)
    transport = TSocket.TSocket(addr,port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = cvService.Client(protocol)
    return transport,client


if __name__=="__main__":
    import os
    try:
        transport,client = getClient()
        transport.open()
        path = './data/cv_51job/'
        fnames = [ path+fname for fname in os.listdir(path)][-20:]
        for fname in fnames:
            cv_html = codecs.open(fname,'rb','utf-8').read()
            result = client.parseHtml(htmlContent = cv_html,cvFrom=fname)
            # 获取结果测试，可删除
            print '=='*20,fname
            print result 
        transport.close()
    except Thrift.TException,e:
        print '%s'%(e.message)
        print 'error',"--"*20

