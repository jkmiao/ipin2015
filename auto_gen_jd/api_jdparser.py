#!/usr/bin/env python
# coding=utf-8

import requests
import simplejson as json
from collections import OrderedDict
import codecs
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

def jdparser(jdstr):
    """
    输入jd文本，返回解析结果，字典形式
    @param jdstr=输入jd的文件名
    @return dict() 字典
	inc_name ( 公司名称 ) :
	inc_tag ( 有关公司的行业性质、员工规模等公司概述信息标签 ) :
	pub_time ( 发布时间 ) :
	end_time ( 截止时间 ) :
	job_name ( 职业名称 ) :
	job_tag ( 有关招聘多少人等、需具备的经验等工作概述信息标签 ) :
	sex ( 性别要求 ) :
	age ( 年龄要求 ) :
	major ( 专业要求 ) :
	degree ( 学历要求 ) :
	exp ( 经验年限要求 ) :
	skill ( 技能要求 ) :
	workplace ( 工作地点 ) :
	pay ( 薪酬待遇 ) :
	cert ( 证书要求(如:英语四六级等级证书) ) :
	demand ( 工作要求 ) :
	duty ( 工作内容 ) :
	benefits ( 福利制度 ) :
	other ( 其它未处理的句子(如公司简介) ) :
    """

    LABELLIST = ["inc_name","inc_tag","pub_time","end_time","job_name","job_tag","sex","age","degree","major","exp","pay","skill","duty","demand","benefits","cert","workplace","other"]
    sort_result = OrderedDict()
    for label in LABELLIST:
        sort_result[label] = ""

    url = 'http://192.168.1.91:8086/string'
    res = requests.post(url,data={"source":jdstr})
    result = json.loads(res.content)
    for label in LABELLIST:
        sort_result[label] = result[label]
    return sort_result



def test(fname='./data/jd_text.txt'):
    jdstr = ""
    if len(sys.argv)==2:
        fname = sys.argv[1]
    else:
        fname = 'data/jd_text.txt'
        
    if os.path.exists(fname):
        jdstr = codecs.open(fname,'rb','utf-8').read()
    else:  
        raise ValueError,'can not open file %s, invalid argument'%fname
		
    result = jdparser(jdstr)
    for key,value in result.iteritems():
        print key
        print value


if __name__=="__main__":
    test(fname='data/jd_text.txt')
