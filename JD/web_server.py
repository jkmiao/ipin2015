#! /user/bin/env python
# -*- coding: utf-8 -*-
import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import JD_extr
from tornado.options import define, options


define("port", default=8081, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('input.html')

class JdExtrHandler(tornado.web.RequestHandler):
    def input(self, text):
        self.render("input.html")

    def post(self):

        source_text = self.get_argument("source")
        result = extr.extr_info(source_text)
        outStr = ""
        outStr +="性别： "+  result["sex"]+"\n"
        outStr += "年龄："+result["age"]+"\n"
        outStr += "专业："+result["major"]+"\n"
        outStr += "学历："+result["degree"]+"\n"
        outStr += "经验："+str(result["exp"])+"年以上\n"
        outStr += "技能："+result["skill"]+"\n"
        outStr += "其他："+result["req"]+"\n" 
        self.render("output.html",source = source_text,result=outStr)

class StringHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('input.html')
#
    def post(self):
        source_text = self.get_argument('source')
#        source_text_Trip = Trip.Trip(source_text.encode('utf-8')).decode('utf-8')
# #       print type(source_text)
#        extr.getstring(source_text.encode('utf-8'))
        reqstr = extr.processing(source_text)
        string = ''
        string  += str(reqstr[u'sex'])+'\t'
        string += str(reqstr[u'age'][0])+' '+str(reqstr[u'age'][1])+'\t'
        string += reqstr[u'degree'] + '\t'
        string += str(reqstr[u'exp']) + '\t'
        string += reqstr[u'major'] +'\t'
        string += reqstr[u'skill']+'\t'
        self.write(string)


extr =JD_extr.JD_extractor()
if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r'/', IndexHandler), (r'/output', JdExtrHandler)],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
