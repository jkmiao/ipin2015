#!/usr/bin/env python
# coding=utf-8

import os.path
import tornado.httpserver
import tornado.options
import tornado.web
from get_job_score  import GenJobScore
from tornado.options import define,options
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

define("port",default=8090,help="run on the given port",type=int)

class RankJobHandler(tornado.web.RequestHandler):
    def get(self):
        domain = self.get_argument("domain",14)
        jobname = self.get_argument("jobname","ios开发")
        self.render('inputgen.html',domain=domain,jobname=jobname,domain_hint=genjd.domain_dict)

    def post(self):
        domain = self.get_argument("domain",14)
        jobname = self.get_argument("jobname","ios开发")
        result = genjd.cal_job_score(jobname,domain)
        self.render('outputgen.html',jobname=jobname,domain=domain,result=result,domain_hint=genjd.domain_dict)



if __name__ == "__main__":
    genjd = GenJobScore()

    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers = [(r'/rankjob',RankJobHandler),(r'/',RankJobHandler)],
        template_path = os.path.join(os.path.dirname(__file__),"templates"),
        debug = True,
        autoescape = None,
        )
    print 'starting tornado at port 8090... '
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
