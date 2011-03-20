#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: model 
# author: dreampuf

import logging
import cPickle as pickle
from hashlib import md5

from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.ext.db import Model
run_in_transaction = db.run_in_transaction
Rollback = db.Rollback
Key = db.Key

from django.dispatch import dispatcher

from cache import memcache

def sendsignal(signal=dispatcher.Any, *arg, **kw):
    dispatcher.send(signal=signal, *arg, **kw)

def with_transaction(func):
    def wapper(*arg, **kw):
        with_transaction = kw.pop("with_transaction", True)
        if with_transaction:
            return db.run_in_transaction(wapper, with_transaction=False, *arg, **kw)
        return func(*arg, **kw)
    return wapper

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
class Setting(Model):
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

    #def __getattr__(self, attrname):
    #    real = Setting.get(self.name, self.default, self.usermemorycache)
    #    return real.__getattr__(attrname)

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

class BaseModel(Model):
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
    
    @classmethod
    def refresh_total(cls, func=None):
        if func:
            tname = "%s_%s::%s" % (TABLE_COUNT_TAG_PRE, cls.__name__, func2str(func)) 
        else:
            tname = "%s_%s" % (TABLE_COUNT_TAG_PRE, cls.__name__)
        tval = cls.all().count(None)
        Setting.set(tname, tval, False)



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

    @classmethod
    def check(cls, email, password):
        user = cls.get_by_key_name(email)
        if user and user.password == md5(password).hexdigest():
            return user
        return None

    @classmethod
    def by_email(cls, email):
        return User.get_by_key_name(email)

class Category(BaseModel):
    ishidden = db.BooleanProperty(default=False)

    title = db.StringProperty()
    description = db.StringProperty(indexed=False)
    order = db.IntegerProperty(default=0)
    belong = db.SelfReferenceProperty(collection_name="children")
    #url = db.StringProperty()    #key_name as url

    @classmethod
    def get_all(cls):
        return cls.all().order("order")

    @classmethod
    def get_categories(cls):
        cates = cls.get_all()
        return [{"url": "/category/%s/"%i.key().name(), "title": i.title } for i in cates]

    @classmethod
    @with_transaction
    def new(cls, url, title, description, order=0, belong=None, with_transaction=True):
        c = cls(key_name=url,
                title=title,
                description=description,
                order=order,
                belong=belong)
        return db.put(c) 

    @classmethod
    def id(cls, cid):
        return cls.get_by_id(cid)

    @classmethod
    def keyname(cls, ckey):
        return cls.get_by_key_name(ckey)
#        cls.incr_counter("%s_%s" % (TABLE_COUNT_TAG_PRE, cls.__name__))

class Tag(BaseModel):
    # key_name as title
    count = db.IntegerProperty(default=1)
 
    @property
    def posts(self):
        return Post.all().filter("tags =", self.key().name()) 

    @classmethod
    def Incr(cls, tag):
        t = cls.get_by_key_name(tag)
        if not t:
            t = cls(key_name=tag)
            t.put()
        else:
            t.count = t.count + 1
            t.put()

    @classmethod
    def Decr(cls, tag):
        t = cls.get_by_key_name(tag)
        if t:
            if t.count == 1:
                db.delete(t)
            else:
                t.count = t.count - 1
                db.put(t)

class PostStatus(object):
    NORMAL = 0
    HIDDEN = 1
    TOP = 2
    PAGE = 3

class PostFormat(object):
    PLAIN = "html"               #like HTML, txt
    MARKDOWN = "markdown"        #markdown
    RST = "rest"                 #ReStructuredText
    UBB = "bbcode"               #UBB

class PostSignals(object):
    New = "Post.New"

class Post(BaseModel):
    """ url 只是存在一个可能的别名,实际匹配时则直接匹配realurl """
    #key_name=realurl, 因为realurl存在修改的可能而key_name无法修改;可能需要key_id数字索引;realurl需要存储之后才能获得; 
    status = db.IntegerProperty(default=PostStatus.NORMAL)
    enablecomment = db.BooleanProperty(default=True)
    format = db.StringProperty(default=PostFormat.PLAIN, indexed=False) # 解析格式
    realurl = db.StringProperty(default="")

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

    @classmethod
    @with_transaction
    def new(cls, title, category_keyname, author_keyname, url, keyword, tags, content, status=PostStatus.NORMAL, format=PostFormat.PLAIN, enablecomment=True):
        c = Key.from_path("Category", category_keyname)
        a = Key.from_path("User", author_keyname)
        
        p = cls(title=title,
                category=c,
                author=a,
                url=url,
                keyword=keyword,
                tags=tags,
                content=content,
                format=format,
                enablecomment=enablecomment )

        deferred.defer(sendsignal, signal=PostSignals.New)

        return db.put(p)

    @classmethod
    @with_transaction
    def modify(cls, post_id, title, category_keyname, author_keyname, url, keyword, tags, content, status=PostStatus.NORMAL, format=PostFormat.PLAIN, enablecomment=True):
        p = cls.id(post_id)
        #cur_tags = set(tags)
        #old_tags = set(p.tags)
        #for i in old_tags^(cur_tags&old_tags):
        #    Tag.Decr(i)
        #for i in cur_tags^(cur_tags&old_tags):
        #    Tag.Incr(i)

        c = Key.from_path("Category", category_keyname)
        a = Key.from_path("User", author_keyname)
        
        p.title=title
        p.category=c
        p.author=a
        p.url=url
        p.keyword=keyword
        p.tags=tags
        p.content=content
        p.format=format
        p.enablecomment=enablecomment
        return db.put(p)

    @classmethod
    def id(cls, pids):
        return Post.get_by_id(pids)

    @classmethod
    def get_by_path(cls, path, keys_only=False):
        return Post.all(keys_only=keys_only).filter("realurl =", path).get()



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




