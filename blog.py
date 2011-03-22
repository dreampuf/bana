#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: blog 
# author: dreampuf

import sys, os, logging 

CURPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(CURPATH, "lib"))

from google.appengine.api import memcache
from google.appengine.ext.webapp import util

import que
from common import BlogHandler 
from blog_views import IndexHandler
from blog_views import CategoryHandler
from blog_views import ViewHandler
from blog_views import CommentHandler

def main():
    application = que.WSGIApplication([("^/$", IndexHandler),
                                       ("^/category/(?P<category_key_name>.*)/$", CategoryHandler),
                                       ("^/comment/(?P<post_id>\d*)/$", CommentHandler),
                                       ("^/(?P<path>.*)$", ViewHandler) ])

    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
