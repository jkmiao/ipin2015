#!/usr/bin/env python
# coding=utf-8


import simplejson as json
import requests
import sys,codecs
reload(sys)
sys.setdefaultencoding('utf-8')

class NerApi(object):
    def __init__(self):
        self.NER_URL = 'http://api.bosonnlp.com/ner/analysis'
        self.API_TOKEN ='UYTG1Csb.3652.5pZ2otkIncEn'
        self.headers = {'X-Token':self.API_TOKEN}


    def get_company(self,jdstr):
        data = json.dumps(jdstr)
        resp = requests.post(self.NER_URL,headers=self.headers,data=data)
        for item in resp.json():
            for entity in item['entity']:
                if entity[2]=='location':
                    print ' '.join(item['word'][entity[0]:entity[1]]),entity[2]




if __name__ == "__main__":
    test = NerApi()
    jdstr = [line.strip() for line in codecs.open('./data/jd_text.txt','rb','utf-8') if len(line)>2 ]
    print('input')
    print('\n'.join(jdstr))
    test.get_company(jdstr)

