#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: template 
# author: dreampuf

import sys, os, logging
CURPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))
#sys.path.insert(0, os.path.join(CURPATH, "lib"))

from google.appengine.ext.webapp import util

from config import BLOG_PATH, TEMPLATE
import que

class aHandler(que.RequestHandler):
    def get(self, filename): #TODO 凑合
        #logging.info(filename)
        tplpath = os.path.join( "..", "static", "views", "iphonsta")
        fs = open(os.path.join(tplpath, filename))
        self.write(fs.read())
        fs.close()
        

def main():
    tpl_path = "%stemplate/%s/(.*)" % (BLOG_PATH ,TEMPLATE )
    application = que.WSGIApplication([
    (tpl_path, aHandler), 
     ])

    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()