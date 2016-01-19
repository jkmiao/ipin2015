#!/usr/bin/env python
# coding=utf-8

import os.path
import tornado.httpserver
import tornado.options
import tornado.web
from auto_gen_jd import AutoGenJD
from jd_parser import JdParser
from tornado.options import define,options
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

define("port",default = 8086,help="run on the given port",type=int)



class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        result = self.get_argument("result",[])
        num = self.get_argument("num",5)
        source_text = self.get_argument("source","")
        self.render("inputgen.html",source = source_text,result = result,num=num)


    def post(self):
        result = self.get_argument("result",[])
        source_text = self.get_argument("source","")
        num = self.get_argument("num",5).encode("utf-8")
        result = genjd.get_jd_with_kmeans(source_text,num)
        self.render("outputgen.html",source = source_text,result = result,num=num)
    


class GenJdHandler(tornado.web.RequestHandler):
    def get(self):
        result = self.get_argument("result",[])
        num1 = self.get_argument("duty_num",4)
        num2 = self.get_argument("demand_num",6)
        num3 = self.get_argument('skill_num',6)
        jobname = self.get_argument("jobname","")
        self.render("inputgen.html",jobname = jobname,result = result,duty_num=num1,demand_num=num2,skill_num=num3)


    def post(self):
        jobname = self.get_argument("jobname","")
        num1 = self.get_argument("duty_num",4).encode('utf-8')
        num2 = self.get_argument("demand_num",6).encode('utf-8')
        num3 = self.get_argument("skill_num",6).encode('utf-8')
        result = genjd.get_jd_with_kmeans(jobname,num1,num2,num3)
        result2 = {}
        # genjd.get_jd_with_textrank(jobname,num1,num2,num3)
        self.render("outputgen.html",jobname = jobname,duty_num=num1,demand_num=num2,skill_num=num3,result=result,result2=result2)


class JdParserHandler(tornado.web.RequestHandler):
    def get(self):
        result = self.get_argument("result",{})
        source_text = self.get_argument("source","")
        self.render("inputjd.html",source=source_text,result=result)


    def post(self):
        upload_path = os.path.join(os.path.dirname(__file__),'files')
        if 'jdfile' in self.request.files:
            file_metas = self.request.files["jdfile"]
            for meta in file_metas:
                filename = meta['filename']
                filepath = os.path.join(upload_path,filename)
                with open(filepath,'wb') as fw:
                    jdstr = meta['body'] 
                    fw.write(jdstr)
                source_text = jdstr
        else:
            source_text = self.get_argument("source","")

        if len(source_text)<5:  
            result = {'error':'input is too short'}
        else:
            result = extr.parser(source_text)
            result['inc_tag'] = ' \n '.join(result['inc_tag'])
            result['job_tag'] = ' \n '.join(result['job_tag'])
            result['skill'] = ' / '.join(result['skill'])
            result['major'] =' / '.join(result['major'])
            result['cert'] = ' / '.join(result['cert'])


        if not result.has_key('error'):
            hintvalue = ["公司名称","有关公司的行业性质、员工规模等公司概述信息标签","发布时间","截止时间","职业名称","有关招聘多少人等、需具备的经验等工作概述信息标签",\
                         "性别要求","年龄要求","专业要求","学历要求","经验年限要求","技能要求","工作地点","薪酬待遇","证书要求(如:英语四六级等级证书)","工作要求","工作内容",\
                        "福利制度","其它未处理的句子(如公司简介)"]
            hintdict = dict((key,value) for (key,value) in zip(result.keys(),hintvalue))
        else:
            hintdict={'error':'sorry,some errors'}
        self.render("outputjd.html",source=source_text,result=result,hint=hintdict)


class StringHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('inputjd.html')

    def post(self):
        source_text = self.get_argument('source').encode('utf-8')
        result = extr.parser(source_text)
        self.write(result)


class MatchHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('match.html',jd="",cv="",result={})

    def post(self):
        jd = self.get_argument("jd","").encode('utf-8')
        cv = self.get_argument("cv","").encode('utf-8')
        res = {}
        if len(jd)>5 and len(cv)>5:
            jd_skill = extr.parser(jd)['skill']
            cv_skill = extr.parser(cv)['skill']
            res = extr.match(jd_skill,cv_skill)
        else:
            res = {'error':'input is too short,length must >5 '}
        self.render("match.html",jd=jd,cv=cv,result=res)



if __name__ == "__main__":
    
    genjd = AutoGenJD()
    extr = JdParser()
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers = [(r'/',GenJdHandler),(r"/genjd",GenJdHandler),(r'/jdparser',JdParserHandler),(r'/string',StringHandler),(r'/match',MatchHandler)],
        template_path = os.path.join(os.path.dirname(__file__),"templates"),
        debug=True,
        autoescape=None,
        )
    print "starting tornado..."
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()



