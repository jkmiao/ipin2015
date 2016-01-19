#!/usr/bin/env python
# coding=utf-8

import sys

sys.path.append('../api_jdparser.py/gen-py/')

import jd.JD_Parser as jdService
from jd.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

def getClient(addr='192.168.1.169',port=9096):
    transport = TSocket.TSocket(addr,port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = jdService.Client(protocol)
    return transport,client


if __name__=="__main__":
    try:
        transport,client = getClient()
        transport.open()
        jdstr = open('../data/jd_text.txt').read()
        print 'jdstr',jdstr
        result = client.parser(jdstr)
        print 'result',result

        for k,v in result.iteritems():
            print k,v
        print 'done'
        
        transport.close()
    except Thrift.TException,e:
        print '%s'%(e.message)

