#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: common 
# author: dreampuf

import cgi, os, logging, sys, string, random
import datetime
import urllib
import wsgiref.handlers

from google.appengine.api import memcache
from google.appengine.ext import deferred
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from django.utils import simplejson as json
from django.dispatch import dispatcher


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
from model import PostSignals 

pjoin = os.path.join
tplengine = tenjin.Engine(path=[pjoin("static", "views"), pjoin("static", "views", "iphonsta")], preprocess=True)  
tplengine_cache_store = tenjin.gae.helpers.fragment_cache.store
tplengine_cache_prefix = tenjin.gae.helpers.fragment_cache.prefix
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
tenjin.logger = logger 

COOKIE_KEY = "0883ba4c4fd211e0a727485b39b890e1"   #this is your code 
def session_middleware(app):
    from google.appengine.ext.appstats import recording  #for developing
    app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
    app = recording.appstats_wsgi_middleware(app)
    return app

def attach_event(func, signal):
    dispatcher.connect(func, signal=signal)

def rPost_tpl_content(post, *args, **kw):
    tplengine_cache_store.set("%spost:content:%s" % (tplengine_cache_prefix, post.key().id()),
                              format_content(post.content, post.format),
                              config.POST_CACHE_TIME )
attach_event(rPost_tpl_content, PostSignals.Modify)

def format_content(content, format="html"):
    if format == "html":
        return content
    elif format == "rest":
        try:
            from docutils.core import publish_parts
        except ImportError, ex:
            sys.path.insert(0, pjoin(config.CURPATH, "lib"))
            from docutils.core import publish_parts
        doc = publish_parts(content ,writer_name='html', settings_overrides= {"file_insertion_enabled": 0,
                                                                              "raw_enabled": 0,
                                                                              "_disable_config": 1, })
        return doc["body"]
    elif format == "markdown":
        try:
            from markdown import markdown
        except ImportError, ex:
            sys.path.insert(0, pjoin(config.CURPATH, "lib"))
            from markdown import markdown
        return markdown(content, output_format="html4")
    elif format == "bbcode":
        try:
            from postmarkup import render_bbcode
        except ImportError, ex:
            sys.path.insert(0, pjoin(config.CURPATH, "lib"))
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
        "%year%": lambda p: p.date_created.year,
        "%month%": lambda p: p.date_created.month,
        "%day%": lambda p: p.date_created.day,
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
        return dt.strftime(format.encode("utf-8"))

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

ISO_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def urlrequest(url, data=None, method=urlfetch.GET, headers=None):
    if data:
        data = urllib.urlencode(data)

    if headers is None:
        headers = {}
    return urlfetch.fetch(url=url,
                          payload=data,
                          method=method,
                          headers=headers).content

def sitemap_time_format(dt):
    if dt.tzinfo:
        dt = dt.astimezone(UTC)
    return dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')

def ISO_FORMAT(dt):
    logging.info(repr(dt))
    if dt.tzinfo:
        return UTCtoLocal(dt).strftime(ISO_TIME_FORMAT)
    else:
        return dt.strftime(ISO_TIME_FORMAT)

def iso_time_now():
    return datetime.utcnow().strftime()

class BaseHandler(que.RequestHandler):
    def __init__(self, request, response, default_status=405):
        #response.header["charset"] = config.CHARSET
        response.set_content_type()
        super(BaseHandler, self).__init__(request, response, default_status)
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

manage_pages = [
        { "url" : config.BLOG_ADMIN_PATH + "logout/", "title" : u"登出" },

        ]

class AdminHandler(BaseHandler):
    def __init__(self, request, response, default_status=405):
        self.session = get_current_session()        
        #self.session["curr_ukey"] = "soddyque@gmail.com"
        #soddy()
        super(AdminHandler, self).__init__(request, response, default_status=405)

    def before(self, *args, **kw):
        if not self.session.get("curr_ukey"):
            self.redirect(config.BLOG_ADMIN_PATH + "login/")
            return

        super(AdminHandler, self).before(*args, **kw)

    def render(self, tplname, context=None, globals=None, layout=False):
        context = context or {}
        context["categories_title"] = u"管理"
        context["pages_title"] = u"其他"
        context["categories"] = manage_categories
        context["pages"] = manage_pages
        
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












