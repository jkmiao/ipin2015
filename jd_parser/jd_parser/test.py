#!/usr/bin/env python
# coding=utf-8

import sys
import threading
reload(sys)
sys.setdefaultencoding('utf-8')



def fun(num):
    for i in range(num):
        print "i am ",threading.currentThread().getName()


def main(thread_num=5):
    thread_list = list()
    for i in range(thread_num):
        thread_name = "thread_%s"%i
        thread_list.append(threading.Thread(target=fun,name=thread_name,args=(5,)))

    for t in thread_list:
        t.start()

    for thread in thread_list:
        t.join()


main(5)



