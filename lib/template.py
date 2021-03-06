#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: template 
# author: dreampuf

import sys, os, logging
CURPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))
#sys.path.insert(0, os.path.join(CURPATH, "lib"))

from google.appengine.ext.webapp import util

from config import config
import que

class aHandler(que.RequestHandler):
    def get(self, filename): #TODO 凑合
        #logging.info(filename)
        if filename.endswith("js"):
            self.set_content_type("text/javascript")
        elif filename.endswith("css"):
            self.set_content_type("text/css")
        self.response.header["Cache-Control"] = "public, max-age=10800"
        tplpath = os.path.join( "..", "static", "views", "iphonsta")
        try:
            fs = open(os.path.join(tplpath, filename))
            self.write(fs.read())
            fs.close()
        except:
            pass
        

def main():
    tpl_path = "%stemplate/%s/(.*)" % (config.BLOG_PATH , config.TEMPLATE )
    application = que.WSGIApplication([
    (tpl_path, aHandler), 
     ])

    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
