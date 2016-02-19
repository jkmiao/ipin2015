#!/usr/bin/env python
# coding=utf-8


from multiprocessing import Pool
import time,os

def fun(x):
    print 'fun',os.getpid()
    time.sleep(1)
    
    return x*x


if __name__ == "__main__":
    pools = Pool(processes=4)
    a = range(1,100)
    result = pools.map(fun,a)
    print result
