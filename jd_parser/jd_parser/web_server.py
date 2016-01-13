#!/usr/bin/env python
# coding=utf-8

import tornado.httpserver
import tornado.options
import tornado.web
from tornado.options import define,options

import sys,os,re

from api_jd_parser import JdParser


reload(sys)
sys.setdefaultencoding('utf-8')

define("port",default=8088,help="run on the given port",type=int)


class JdParserHandler(tornado.web.RequestHandler):
    def get(self):
        result = self.get_argument("result",{})
        source_text = self.get_argument("source","")
        self.render("inputjd.html",source=source_text,result=result)


    def post(self):
        source_text = self.get_argument("source","")
        if re.search("www.lagou.com/jobs/\d+.html",source_text):
            result = jdParser.jd_parser_lagou.parser(url=source_text)

        elif re.search(u"jobs.zhaopin.com/.+\d+.htm",source_text):
            result = jdParser.jd_parser_zhilian.parser(url=source_text)

        elif re.search("jobs.51job.com/.+\d+.htm",source_text):
            result = jdParser.jd_parser_51job.parser(url=source_text)
        
        elif re.search("job.liepin.com/\d+",source_text):
            result = jdParser.jd_parser_liepin.parser(url=source_text)

        else:
            print 'url',source_text
            result = {'error':'input url is wrong','url':source_text}

        self.render("outputjd.html",source=source_text,result=result)




class JdUrlHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            source_text = self.get_argument("input_url")

            if re.search("www.lagou.com/jobs/\d+.html",source_text):
                result = jdParser.jd_parser_lagou.parser(url=source_text)

            elif re.search(u"jobs.zhaopin.com/.+\d+.htm",source_text):
                result = jdParser.jd_parser_zhilian.parser(url=source_text)

            elif re.search("jobs.51job.com/.+\d+.htm",source_text):
                result = jdParser.jd_parser_51job.parser(url=source_text)

            elif re.search("job.liepin.com/\d+",source_text):
                result = jdParser.jd_parser_liepin.parser(url=source_text)
            else:
                result ={ "error":"input url is wrong",'url:':source_text }
        except Exception,e:
            result ={ "error":"sorry,sth wrong happened","reason":e }
            
        self.write(result)


class JdStringHandler(tornado.web.RequestHandler):

    def post(self):
        try:
            htmlContent = self.get_argument("htmlContent","")
            jdFrom = self.get_argument("jdFrom","")
            result = jdParser.parser(htmlContent = htmlContent,jdFrom=jdFrom)
        except Exception,e:
            result ={ "error":str(e)}
        self.write(result)




if __name__ == "__main__":

    jdParser = JdParser()
    

    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers = [(r'/',JdParserHandler),(r'/jdparser',JdParserHandler),(r"/jdUrl",JdUrlHandler)],
        template_path = os.path.join(os.path.dirname(__file__),"templates"),
        debug=True,
        autoescape=None,
        )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    print "starting tornado at port %d..." % options.port
    tornado.ioloop.IOLoop.instance().start()



