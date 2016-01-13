#!/usr/bin/env python
# coding=utf-8

import sys

import ipin.rpc.etl.jd.analyze.JdAnalyzeService as jdService
from ipin.rpc.etl.jd.jd_type.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
import codecs



def getClient(addr='192.168.1.91',port=9099):
    print 'conneting server %s at port %d' %(addr,port)
    transport = TSocket.TSocket(addr,port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = jdService.Client(protocol)
    return transport,client






if __name__=="__main__":
    try:
        transport,client = getClient()
        transport.open()

        fname = './test_jds/zhilian/zhilian_jd_102.html'
        jd_html = codecs.open(fname,'rb','utf-8').read()
        print 'parsing...'

        result = client.analyzeHtml(jd_html,jdFrom=fname)

        # 获取结果测试，可删除
        print result
        
        transport.close()

    except Thrift.TException,e:
        print '%s'%(e.message)

