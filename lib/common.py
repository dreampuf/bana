#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: common 
# author: dreampuf

import cgi, os, logging, sys, string, random
import datetime
import wsgiref.handlers

from google.appengine.api import memcache
from google.appengine.ext import deferred
from google.appengine.ext.webapp import util
from django.utils import simplejson as json


from config import config
import que
#from config import CURPATH
import tenjin
tenjin.gae.init()
from tenjin.helpers import *
escape , to_str = tenjin.helpers.escape, tenjin.helpers.to_str
from gaesession import SessionMiddleware, get_current_session 

from model import User

pjoin = os.path.join
tplengine = tenjin.Engine(path=[pjoin("static", "views", "iphonsta")], cache=tenjin.MemoryCacheStorage(), preprocess=True)  


COOKIE_KEY = "0883ba4c4fd211e0a727485b39b890e1"   #this is your code 

def session_middleware(app):
    from google.appengine.ext.appstats import recording  #for developing
    app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
    app = recording.appstats_wsgi_middleware(app)
    return app

def randstr(start=5, end=10, case=string.lowercase):
    return "".join([random.choice(case) for i in xrange(random.randint(start, end))])

def soddy():
    soddy = User.get_by_key_name("soddyque@gmail.com")
    if not soddy:
        soddy = User(key_name="soddyque@gmail.com", nickname=u"米落", password="123")  
        soddy.put()
    return soddy

url_mapper = {
        "%category%": lambda p: p.category.title,
        "%year%": lambda p: p.created.year,
        "%month%": lambda p: p.created.month,
        "%day%": lambda p: p.created.day,
        "%title%": lambda p: p.title,
        "%url%": lambda p: p.url,
        "%author%": lambda p: p.author.nickname,
}
def realurl(post):
    url = config.POST_URL
    for key, val in mapper.items():
        if url.find(key) != -1:
            url = url.replace(key, str(val(post)))
    return url

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

    def jsonout(self, obj):
        self.set_content_type("json")
        self.write(json.dumps(obj))


manage_categories = [
        { "url" : config.BLOG_ADMIN_PATH + "post/new/", "title": u"添加文章" },
        { "url" : config.BLOG_ADMIN_PATH + "post/", "title" : u"文章管理" },
        { "url" : config.BLOG_ADMIN_PATH + "reply/", "title" : u"评论" },
        { "url" : config.BLOG_ADMIN_PATH + "config/", "title" : u"站点配置" },

        ]

class AdminHandler(BaseHandler):
    def __init__(self, request, response, default_status=405):
        request.session = get_current_session()        
        request.session["curr_ukey"] = "soddyque@gmail.com"
        soddy()
        super(AdminHandler, self).__init__(request, response, default_status=405)

    def render(self, tplname, context=None, globals=None, layout=False):
        context = context or {}
        context["categories_title"] = u"管理"
        context["pages_title"] = u"其他"
        context["categories"] = manage_categories
        
        super(AdminHandler, self).render(tplname, context, globals, layout)

    def curr_ukey(self):
        return self.request.session.get("curr_ukey", None)

class BlogHandler(BaseHandler):
    pass 












