#!/usr/bin/env python
# coding=utf-8

import tornado.httpserver
import tornado.options
import tornado.web
from tornado.options import define,options

import simplejson as json
from api_cv_parser import CvParser

import sys,os,re

reload(sys)
sys.setdefaultencoding('utf-8')

define("port",default=8087,help="run on the given port",type=int)


class CvParserHandler(tornado.web.RequestHandler):
    def get(self):
        result = self.get_argument("result",{})
        source_text = self.get_argument("source","")

        self.render("inputcv.html",source=source_text,result=result)


    def post(self):
        source_text = self.get_argument("source","")

        if "cvfile" in self.request.files:
            file_metas = self.request.files["cvfile"]
            for meta in file_metas:
                source_text = meta["body"]

            if re.search(u"zhaopin.com",source_text):
                result = cv_parser.cv_parser_zhilian.parser(htmlContent=source_text)

            elif re.search("jianli.m.58.com",source_text):
                result = cv_parser.cv_parser_58.parser(htmlContent=source_text)

            elif re.search(u"51job",source_text):
                result = cv_parser.cv_parser_51job.parser(htmlContent=source_text)

            else:
                result = {"error":"upload file error!"}

        else:
            if re.search("http://jianli.58.com/resume",source_text):
                result = cv_parser.cv_parser_58.parser(url=source_text)
            
            elif len(source_text)<10:
                result = {'error':'input url is wrong'}


        result = json.dumps(result,ensure_ascii=False,indent=4)

        self.render("outputcv.html",source=source_text,result=result)


class StringHandler(tornado.web.RequestHandler):

    def post(self):
        htmlContent = self.get_argument('htmlContent',"")
        cvFrom = self.get_argument("cvFrom","")
        
        result = cv_parser.parser(htmlContent=htmlContent,cvFrom=cvFrom)
        result = json.dumps(result,ensure_ascii=False,indent=4)

        self.write(result)




cv_parser = CvParser()

if __name__ == "__main__":

    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers = [(r'/',CvParserHandler),(r'/cvparser',CvParserHandler),(r'/string',StringHandler)],
        template_path = os.path.join(os.path.dirname(__file__),"templates"),
        debug=True,
        autoescape=None,
        )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    print "starting tornado at port %d..." % options.port
    tornado.ioloop.IOLoop.instance().start()



