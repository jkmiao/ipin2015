#!/usr/bin/env python
# coding=utf-8

import tornado.ioloop
import tornado.web
import json
from jd_parser import JdParser

class StringHandler(tornado.web.RequestHandler):
    def post(self):
        source_text = self.get_argument('source').encode('utf-8')
        result = clf.predict(source_text)
        self.write(json.dumps(result))


app = tornado.web.Application(
    handlers = [('r/string',StringHandler)]
    )

clf = JdParser() 
if __name__ == "__main__":
    app.listen(8080)
    print 'starting tornado'
    tornado.ioloop.IOLoop.instance().start()
