#!/usr/bin/env python
# coding=utf-8

import json,re
import requests
from tgrocery import Grocery

def svmclf(jdstr="",url="192.168.1.92:8080"):
    res = requests.post(url,data={'source':jdstr})
    result = json.loads(res.content)
    print result
    return result



class jdParser(object):

    def __init__(self):
        self.clf = Grocery("./jdclf")
        self.clf.load()
        self.LINE_SPLIT = re.compile(u"[；。;\n]")



    def get_demand_and_duty(self,jdstr):
        linelist = [ line.strip() for line in self.LINE_SPLIT.split(jdstr) if len(line.strip()>4) ]

        result = {}
        demand = []
        duty = []
        for line in linelist:
            pred = str(self.clf.predict(line))
            if pred =="demand":
                demand.append(line)
            elif pred == "duty":
                duty.append(line)

        result['demand'] = '\n'.join(demand)
        result['duty'] = '\n'.join(duty)

