#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: main 
# author: dreampuf

import sys, os, logging 

CURPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(CURPATH, "lib"))

from google.appengine.api import memcache
from google.appengine.ext.webapp import util

import que
from common import BlogHandler 

from cache import locache
class MainHandler(BlogHandler):
    def get(self):
        self.render("index.html", { "time" : "<strong>cc</strong>ccc"} )
        #write("Hello World!")


def main():
    application = que.WSGIApplication([("^/$", MainHandler)])

    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
