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
from gaesession import SessionMiddleware, get_current_session 


from model import User
from model import Category
from model import Post 

pjoin = os.path.join
tplengine = tenjin.Engine(path=[pjoin("static", "views", "iphonsta")], preprocess=True)  

COOKIE_KEY = "0883ba4c4fd211e0a727485b39b890e1"   #this is your code 
def session_middleware(app):
    from google.appengine.ext.appstats import recording  #for developing
    app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
    app = recording.appstats_wsgi_middleware(app)
    return app

def format_content(content, format="html"):
    if format == "html":
        return content
    elif format == "rest":
        from docutils.core import publish_parts
        doc = publish_parts(content ,writer_name='html', settings_overrides= {"file_insertion_enabled": 0,
                                                                              "raw_enabled": 0,
                                                                              "_disable_config": 1, })
        return doc["body"]
    elif format == "markdown":
        from markdown import markdown
        return markdown(content, output_format="html4")
    elif format == "ubbcode":
        from postmarkup import render_bbcode
        return render_bbcode(content, encoding=config.CHARSET, paragraphs=True)

def randstr(start=5, end=10, case=string.lowercase):
    return "".join([random.choice(case) for i in xrange(random.randint(start, end))])

def soddy():
    soddy = User.get_by_key_name("soddyque@gmail.com")
    if not soddy:
        soddy = User(key_name="soddyque@gmail.com", nickname=u"米落", password="123")  
        soddy.put()
    return soddy

def genid(n):
    while True:
        yield n
        n += 1

def gender_url(url, filter_func=lambda url: Post.get_by_path(url)):
    p = filter_func(url) 
    if not p:
        return url
    genter = genid(1)
    if url.find("/") != -1:
        if url.split("/")[-1].find(".") != -1:
            ori, ext = url[:url.rfind(".")], url[url.rfind("."):]
        else:
            ori, ext = url[:url.rfind("/")], url[url.rfind("/"):]
    elif url.find(".") != -1:
        ori, ext = url[:url.rfind(".")], url[url.rfind("."):]
    else:
        ori, ext = url, ""

    while(filter_func(url)):
        url = "%s%d%s" % (ori, genter.next(), ext)
    return url
    

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
    for key, val in url_mapper.items():
        if url.find(key) != -1:
            url = url.replace(key, str(val(post)))
    return gender_url(url)

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

def FormatTime(dt, format=config.DATETIME_FORMAT):
    if dt:
        return dt.strftime(format)

def ParserTime(dtstr, format="%Y/%m/%d %H:%M:%S"):
    return datetime.datetime.strptime(dtstr, format)

def ParserLocalTimeToUTC(dtstr, format="%Y/%m/%d %H:%M:%S"):
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
        self.session = get_current_session()        
        self.session["curr_ukey"] = "soddyque@gmail.com"
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
    def render(self, tplname, context=None, globals=None, layout=False):
        context = context or {}
        #context["categories_title"] = u"分类"
        #context["pages_title"] = u"其他"
        context["categories"] = Category.get_categories()
        
        super(BlogHandler, self).render(tplname, context, globals, layout)












