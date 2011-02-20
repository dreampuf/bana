#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: 启动文件
# author: dreampuf

import sys, os, logging 

CURPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(CURPATH, "lib"))
#sys.path.append(os.path.join(CURPATH, "lib"))

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from docutils.core import publish_parts

override_setting={
        'file_insertion_enabled':0,
        'raw_enabled':0,
        '_disable_config':1,
        }

doc = """
===========
你好周杰伦
===========

:author:Dreampuf
:date:2011-02-14 01:38:34

谢谢
---------

#. verynice
#. yeah

是的吗?
=======

""很明显是的""

"""

from cache import locache
class MainHandler(webapp.RequestHandler):
    def get(self):
        write = self.response.out.write
        #memcache.set("cc", "gg")
        #dd=publish_parts(doc,writer_name='html',settings_overrides=override_setting)
        #logging.info(dd.keys())
        #self.response.out.write(dd["body"])

        if locache.get("c") is None:
            locache.set("c", 1)
        locache.incr("c")
        write(locache.get("c"))
        


def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
