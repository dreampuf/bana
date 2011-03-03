#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: model 
# author: dreampuf

import logging
import cPickle as pickle
from hashlib import md5

from google.appengine.ext import db
from google.appengine.ext.db import Model as DBModel

from cache import memcache

def memcached(key, cache_time=0, key_suffix_calc_func=None, namespace=None):
    def wrap(func):
        def cached_func(*args, **kw):
            key_with_suffix = key
            if key_suffix_calc_func:
                key_suffix = key_suffix_calc_func(*args, **kw)
                if key_suffix is not None:
                    key_with_suffix = '%s:%s' % (key, key_suffix)

            value = memcache.get(key_with_suffix, namespace)
            if value is None:
                value = func(*args, **kw)
                try:
                    memcache.set(key_with_suffix, value, cache_time, namespace)
                except:
                    pass
            return value
        return cached_func
    return wrap


TABLE_COUNT_TAG_PRE = "tablecount"
_settingcache = {}
class Setting(DBModel):
    name=db.StringProperty()
    value=db.TextProperty()

    @classmethod
    def get(cls,name,default=None, useMemoryCache=True):
        global _settingcache
        if useMemoryCache and _settingcache.has_key(name) :
            return _settingcache[name]
        else:
            n = memcache.get("setting.%s" % name)
            if n != None:
                if useMemoryCache:
                    _settingcache[name] = n
                return n
        try:
            opt=Setting.get_by_key_name(name)
            result = pickle.loads(str(opt.value))

            if useMemoryCache:
                _settingcache[name] = result
            memcache.set("setting.%s" % name, result, 0)
            return result
        except:
            return default

    @classmethod
    def set(cls,name,value, useMemoryCache=True):
        if useMemoryCache:
            global _settingcache
            _settingcache[name] = value

        memcache.set("setting.%s" % name, value, 0)

        opt = Setting.get_or_insert(name)
        opt.name = name
        opt.value = pickle.dumps(value)
        opt.put()

    @classmethod
    def remove(cls,name):
        global _settingcache
        if _settingcache.has_key(name):
            del _settingcache[name]
        memcache.delete("setting.%s" % name, 0)
        opt= Setting.get_by_key_name(name)
        if opt:
            opt.delete()

class _ConfigProperty(object):

    def __init__(self, name, default=None, useMemoryCache=True):
        self.name = "config_%s" % name
        self.default= default
        self.usememorycache = useMemoryCache

    def __get__(self, instance, klass):
        return Setting.get(self.name, self.default, self.usememorycache)

    def __set__(self, instance, value):
        Setting.set(self.name, value, self.usememorycache)
    
    def __str__(self):
        return Setting.get(self.name, self.default, self.usememorycache)

class _Pager(object):
    def __init__(self, data, count, index, last):
        self.data = data
        self.count = count
        self.index = index
        self.prev = index - 1
        self.next = (index + 1 > last) and 0 or (index + 1)
        self.last = last

    def __repr__(self):
        return "<_Pager: count:%s, index:%s, prev:%s, next:%s, last:%s, Entry_Type:%s >" % (self.count, self.index, self.prev, self.next, self.last, self.data[0].__class__.__name__)

def func2str(func):
    fcode = func.func_code
    return md5("%s%s" % (fcode.co_code, fcode.co_consts)).hexdigest()

class BaseModel(DBModel):
    _lastQuery = None

    def put(self, **kw):
        if not self.is_saved():
            tname = "%s_%s" % (TABLE_COUNT_TAG_PRE, self.__class__.__name__ , )
            tval = Setting.get(tname, useMemoryCache=False)
            if tval == None:
                tval = self.__class__.total()
            Setting.set(tname, tval + 1, False)
        super(BaseModel, self).put(**kw)

    def delete(self, **kw):
        if self.is_saved():
            tname = "%s_%s" % (TABLE_COUNT_TAG_PRE, self.__class__.__name__)
            tval = Setting.get(tname, useMemoryCache=False)
            if tval == None:
                tval = self.__class__.all().count(None)
            Setting.set(tname, tval - 1, False)
        super(BaseModel, self).delete(**kw)

    @classmethod
    def puts(cls, entrys):
        tname = "%s_%s" % (TABLE_COUNT_TAG_PRE, cls.__name__)
        Setting.set(tname, cls.total() + len(entrys), False)
        db.put(entrys)

    @classmethod
    def deletes(cls, vals):
        tname = "%s_%s" % (TABLE_COUNT_TAG_PRE, cls.__name__)
        Setting.set(tname, cls.total() - len(vals), False)

        db.delete(vals)

    @classmethod
    def fetch_page(cls, p, plen = 20, func=None):
        total = cls.total(func)
        n = total / plen
        if total % plen != 0:
            n = n + 1
        #logging.info(n)
        if p < 0 or p > n:
            p = 1
        offset = (p - 1) * plen
        query = cls.all() #cls._lastQuery if cls._lastQuery else cls.all()
        results = query.fetch(plen, offset) if func is None else func(query).fetch(plen, offset)
        cls._lastQuery = query
        return _Pager(results, total, p, n)

    @classmethod
    def cursorfetch(cls, cursor, plen = 20, func=None):
        query = cls._lastQuery if cls._lastQuery else cls.all()
        query = func(query) if func else query
        ls = query.with_cursor(cursor)[:plen]        
        cls._lastQuery = query
        return ls 

    @classmethod
    def cursor(cls):
        if cls._lastQuery:
            return cls._lastQuery.cursor()
        return None

    @classmethod
    def total(cls, func=None):
        if func:
            tname = "%s_%s::%s" % (TABLE_COUNT_TAG_PRE, cls.__name__, func2str(func)) 
        else:
            tname = "%s_%s" % (TABLE_COUNT_TAG_PRE, cls.__name__)

        tval = Setting.get(tname, useMemoryCache=False)
        if tval == None:
            logging.info("calc the %s total count" % cls.__name__)
            tval = cls.all().count(None) if func == None else func(cls.all()).count(None)
            Setting.set(tname, tval, False)
        return tval


def toBlob(val):
    return db.Blob(val)

def toLink(val):
    return db.Link(val)

def toEmail(val):
    return db.Email(val)

class User(BaseModel):
    nickname = db.StringProperty(required=True)
    password = db.StringProperty(indexed=False)
    created = db.DateTimeProperty(auto_now_add=True)

    lastip = db.StringProperty(indexed=False)
    lastlogin = db.DateTimeProperty()

    #email = db.EmailProperty() #key_name as email

class Category(BaseModel):
    ishidden = db.BooleanProperty(default=False)

    title = db.StringProperty()
    description = db.StringProperty(indexed=False)
    order = db.IntegerProperty(default=0)
    belong = db.SelfReferenceProperty(collection_name="children")
    #url = db.StringProperty()    #key_name as url

class Tag(BaseModel):
    # key_name as title
    count = db.IntegerProperty(default=0)
 
    @property
    def posts(self):
        return Post.all().filter("tags =", self.key().name()) 

    @classmethod
    def IncrTags(tags):
        #TODO 增加Tag
        pass

    @classmethod
    def DecrTags(tags):
        #TODO 去掉Tag
        pass

class PostStatus(object):
    NORMAL = 0
    HIDDEN = 1
    TOP = 2
    PAGE = 3

class PostFormat(object):
    PLAIN = 0               #like HTML, txt
    MARKDOWN = 1            #markdown
    RST = 2                 #ReStructuredText
    UBB = 3                 #UBB

class Post(BaseModel):
    """ url 只是存在一个可能的别名,实际匹配时则直接匹配realurl(现在存放在key_name中) """

    #realurl = db.StringProperty()   #key_name as realurl
    status = db.StringProperty(default=PostStatus.NORMAL)
    enablecomment = db.BooleanProperty(default=True)
    format = db.IntegerProperty(default=PostFormat.PLAIN, indexed=False) # 解析格式

    category = db.ReferenceProperty(Category, collection_name="posts")
    author = db.ReferenceProperty(User, collection_name="posts")
    title = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    modify = db.DateTimeProperty(auto_now_add=True)
    url = db.StringProperty() 
    keyword = db.StringListProperty() 
    content = db.TextProperty()
    views = db.IntegerProperty(default=0)

    tags = db.StringListProperty()


class CommentType(object):
    COMMENT = "comment"
    TRACKBACK = "trackback"
    PINGBACK = "pingback"

class Comment(BaseModel):
    commenttype = db.StringProperty(default=CommentType.COMMENT)

    belong = db.ReferenceProperty(Post, collection_name="comments")
    author = db.ReferenceProperty(User, collection_name="comments")
    re = db.SelfReferenceProperty(collection_name="children")
    content = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    nickname = db.StringProperty()
    ip = db.StringProperty()
    website = db.LinkProperty()
    email = db.EmailProperty()
    hascheck = db.BooleanProperty(default=True)

class Attachment(BaseModel):
    beuse = db.ReferenceProperty(Post, collection_name="attachments")
    belong = db.ReferenceProperty(User, collection_name="attachments")

    filename = db.StringProperty()
    filetype = db.StringProperty()
    filesize = db.IntegerProperty(default=0)
    content = db.BlobProperty()
    created = db.DateTimeProperty(auto_now_add=True)

    def setfiletype(self, filename):
        self.filetype = os.path.splitext(filename)[1][1:]


class Plugin(BaseModel):
    enable = db.BooleanProperty(default=False)

    pluginguid = db.StringProperty()
    pluginname = db.StringProperty()
    plugintype = db.StringProperty()
    plugindescription = db.StringProperty()
    pluginauthor = db.StringProperty()
    pluginurl = db.LinkProperty()
    pluginsize = db.IntegerProperty(default=0)
    plugindata = db.BlobProperty()




