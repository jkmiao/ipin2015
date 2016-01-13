#!/usr/bin/env python
# coding=utf-8

import os.path
import tornado.httpserver
import tornado.options
import tornado.web
from auto_gen_jd import AutoGenJD
from tornado.options import define,options
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

define("port",default=8088,help="run on the given port",type=int)

class GenJdHandler(tornado.web.RequestHandler):
    def get(self):
        num1 = self.get_argument("duty_num",4)
        num2 = self.get_argument("demand_num",5)
        num3 = self.get_argument("skill_num",6)
        self.render('inputgen.html',duty_num=num1,demand_num=num2,skill_num=num3)

    def post(self):
        jobname = self.get_argument("jobname","")
        num1 = self.get_argument("duty_num",4)
        num2 = self.get_argument("demand_num",5)
        num3 = self.get_argument("skill_num",6)
        result = genjd.get_jd_with_kmeans(jobname,num1,num2,num3)
        self.render('outputgen.html',jobname=jobname,result=result,duty_num=num1,demand_num=num2,skill_num=num3)




if __name__ == "__main__":
    genjd = AutoGenJD()

    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers = [(r'/genjd',GenJdHandler),(r'/',GenJdHandler)],
        template_path = os.path.join(os.path.dirname(__file__),"templates"),
        debug = True,
        autoescape = None,
        )
    print 'starting tornado at port 8088... '
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
