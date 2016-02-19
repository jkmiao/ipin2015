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



def getClient(addr='192.168.1.169',port=9098):
    print 'conneting server %s at port %d' %(addr,port)
    transport = TSocket.TSocket(addr,port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = jdService.Client(protocol)
    return transport,client




if __name__=="__main__":
    import os,jsonpickle,json

    try:
        transport,client = getClient()
        transport.open()

        path = "./test_jds/51job//"
        fnames = [ path + fname for fname in os.listdir(path) if fname.endswith("html") ][:20]
        for fname in fnames:
            print '==='*20,fname
            jd_html = codecs.open(fname,'rb','gb18030').read()
            result = client.analyzeHtml(jd_html,jdFrom=fname)
            # 获取结果测试，可删除
            result = jsonpickle.encode(result,unpicklable = False)
            print json.dumps(jsonpickle.decode(result),ensure_ascii = False, indent=4)
        
        transport.close()

    except Thrift.TException,e:
        print 'error: %s',e

