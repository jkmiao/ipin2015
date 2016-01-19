#!/usr/bin/env python
# coding=utf-8

import sys,os

sys.path.append('./api_jd_parser/gen-py/')
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import jd.JD_Parser as jdService
from jd.ttypes import *
from jd.constants import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from jd_parser import JdParser 

# from jd_parser import JdParser


class JDHandler:

    def __init__(self):
        self.extr = JdParser()
    
    def parser(self,jdstr):
        jdstr = jdstr.encode('utf-8')
        result = self.extr.parser(jdstr)

        for k in result:
            if re.search(u"不限",result[k]):
                result[k] = NO_LIMIT_FIELD
            elif len(result[k].encode('utf-8'))<2:
                print 'k',k
                result[k] = EMPTY_FIELD

            result[k] = result[k].encode('utf-8')
            print k,result[k]

        output = JD_RESULT_DATA(**result)
        return output

    def get_multi(self,jdstr):
        jdstr = jdstr.encode('utf-8')
        result = self.extr.split_multi_jd(jdstr)
        return result



if __name__=="__main__":
    handler = JDHandler()
   # inputstr =  open('./data/jd_text.txt').read()
   # res = handler.parser(inputstr)
   # print "res",res
    processor = jdService.Processor(handler)
    transport = TSocket.TServerSocket(port=9096)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor,transport,tfactory,pfactory)
    print 'Starting the thrift server at port 9096...'
    server.serve()
    print 'done'



