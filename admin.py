#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: admin_url 
# author: dreampuf

import sys, os, logging 
CURPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(CURPATH, "lib"))

from google.appengine.ext.webapp import util

from config import config
from admin_views import LoginHandler
from admin_views import LogoutHandler
from admin_views import AdminIndexHandler
from admin_views import AdminAddPostHandler
from admin_views import AdminConfigHandler
from admin_views import AdminCategoryHandler
from admin_views import AdminPostHandler
from admin_views import AdminModifyPostHandler
from admin_views import AdminCronHandler
from admin_views import AdminUtilHandler
import que
from common import session_middleware


def main():
    BLOG_ADMIN_PATH = config.BLOG_ADMIN_PATH
    application = que.WSGIApplication([
    (BLOG_ADMIN_PATH + "post/", AdminPostHandler), 
    (BLOG_ADMIN_PATH + "post/new/", AdminAddPostHandler),
    (BLOG_ADMIN_PATH + "post/(?P<post_id>\d+)/", AdminModifyPostHandler),
    (BLOG_ADMIN_PATH + "login/", LoginHandler), 
    (BLOG_ADMIN_PATH + "logout/", LogoutHandler), 
    (BLOG_ADMIN_PATH + "config/", AdminConfigHandler), 
    (BLOG_ADMIN_PATH + "category/", AdminCategoryHandler), 
    (BLOG_ADMIN_PATH + "cron/(?P<instruct>\w+)/", AdminCronHandler), 
    (BLOG_ADMIN_PATH + "util/(?P<action>[^/]+)/", AdminUtilHandler), 
    (BLOG_ADMIN_PATH, AdminIndexHandler) ])

    util.run_wsgi_app(session_middleware(application))


if __name__ == '__main__':
    main()
