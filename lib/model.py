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
    def fetch_page(cls, p, plen = 20, fun=None):
        total = cls.total(fun)
        n = total / plen
        if total % plen != 0:
            n = n + 1
        #logging.info(n)
        if p < 0 or p > n:
            p = 1
        offset = (p - 1) * plen
        query = cls._lastQuery if cls._lastQuery else cls.all()
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

class User(BaseModel):
    username = db.StringProperty()
    password = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    lastip = db.StringProperty()
    lastlogin = db.DateTimeProperty()

    email = db.EmailProperty()

    def setEmail(self, val):
        self.email = db.Email(val)

class Category(BaseModel):
    ishidden = db.BooleanProperty(default=False)

    title = db.StringProperty()
    description = db.StringProperty()
    order = db.IntegerProperty(default=0)
    url = db.StringProperty()

class Tag(BaseModel):
    title = db.StringProperty()
    description = db.StringProperty()

    @property
    def posts(self):
        if not hasattr(self, "_posts"):
            self._posts = [i.post for i in self._posts.fetch(1000)]
        return self._posts

    @property
    def postslen(self):
        '''return a integer of post, the post's tags porperty used self'''
        if not hasattr(self, "_postlen"):
            self._postlen = tags_posts.all().filter("tag =", self.key()).count()
        return self._postlen

class PostStatus(object):
    NORMAL = "normal"
    HIDDEN = "hidden"
    TOP = "top"
    PAGE = "page"

class Post(BaseModel):
    status = db.StringProperty(default=PostStatus.NORMAL)
    realurl = db.StringProperty()
    enablecomment = db.BooleanProperty(default=True)

    category = db.ReferenceProperty(Category, collection_name="posts")
    author = db.ReferenceProperty(User, collection_name="posts")
    title = db.StringProperty()
    created = db.DateTimeProperty()
    url = db.StringProperty()
    content = db.TextProperty()
    precontent = db.TextProperty()
    views = db.IntegerProperty(default=0)

    @property
    def tags(self):
        if not hasattr(self, "_ptags"):
            self._ptags = [i.tag for i in self._tags.fetch(1000)]
        return self._ptags

    @classmethod
    def SearchableProperties(cls):
        return [['title', 'content'], ['title'], search.ALL_PROPERTIES]

class tags_posts(BaseModel):
    tag = db.ReferenceProperty(Tag, collection_name="_posts")
    post = db.ReferenceProperty(Post, collection_name="_tags")

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

    def setWebsite(self, val):
        self.website = db.Link(val)

    def setEmail(self, val):
        self.email = db.Email(val)

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
