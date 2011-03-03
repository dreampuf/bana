#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: common 
# author: dreampuf

import cgi, os, logging, sys
import datetime
import wsgiref.handlers

from google.appengine.api import memcache
from google.appengine.ext import deferred

import config
import que
#from config import CURPATH
import tenjin
tenjin.gae.init()
from tenjin.helpers import *
escape , to_str = tenjin.helpers.escape, tenjin.helpers.to_str

pjoin = os.path.join

tplengine = tenjin.Engine(path=[pjoin("static", "views", "iphonsta")], cache=tenjin.MemoryCacheStorage(), preprocess=True)  

ZERO_TIME_DELTA = datetime.timedelta(0)
class LocalTimezone(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=Config.localtimezone)

    def dst(self, dt):
        return ZERO_TIME_DELTA

LOCAL_TIMEZONE = LocalTimezone()

class UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        return ZERO_TIME_DELTA

    def dst(self, dt):
        return ZERO_TIME_DELTA
UTC = UTC()

def ParserTime(dtstr, format = "%Y/%m/%d %H:%M:%S"):
    return datetime.datetime.strptime(dtstr, format)

def ParserLocalTimeToUTC(dtstr, format = "%Y/%m/%d %H:%M:%S"):
    return ParserTime(dtstr, format).replace(tzinfo=LOCAL_TIMEZONE).astimezone(UTC) \
                .replace(tzinfo=None) #fix in Google Engine App


def LocalToUTC(dt):
    if dt.tzinfo:
        dt.replace(tzinfo=None)
    return dt.replace(tzinfo=LOCAL_TIMEZONE).astimezone(UTC)

def UTCtoLocal(dt):
    if dt.tzinfo:
        dt.replace(tzinfo=None)
    return dt.replace(tzinfo=UTC).astimezone(LOCAL_TIMEZONE) \
                .replace(tzinfo=None) #fix in Google Engine App



class BaseHandler(que.RequestHandler):
    def render(self, tplname, context=None, globals=None, layout=False):
        context = context or {}
        context["request"] = self.request
        context["config"] = config
        self.write(tplengine.render(tplname, context, globals, layout))


manage_categories = [
        { "url" : "post/new/", "title": u"添加文章" },
        { "url" : "post/", "title" : u"文章管理" },
        { "url" : "reply/", "title" : u"评论" },
        { "url" : "config/", "title" : u"站点配置" },

        ]

class AdminHandler(BaseHandler):
    def render(self, tplname, context=None, globals=None, layout=False):
        context = context or {}
        context["categories_title"] = u"管理"
        context["pages_title"] = u"其他"
        context["categories"] = manage_categories
        super(AdminHandler, self).render(tplname, context, globals, layout)

class BlogHandler(BaseHandler):
    pass 












