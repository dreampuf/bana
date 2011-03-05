#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: admin_url 
# author: dreampuf

import sys, os 
CURPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(CURPATH, "lib"))

from google.appengine.ext.webapp import util

from config import config
from admin_views import LoginHandler, AdminIndexHandler, AdminAddPostHandler
import que

def main():
    BLOG_ADMIN_PATH = config.BLOG_ADMIN_PATH
    application = que.WSGIApplication([
    (BLOG_ADMIN_PATH + "post/new/", AdminAddPostHandler),
    (BLOG_ADMIN_PATH + "login/", LoginHandler), 
    (BLOG_ADMIN_PATH, AdminIndexHandler) ])

    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
