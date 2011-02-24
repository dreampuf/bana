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

def func2str(func):
    fcode = func.func_code
    return md5("%s%s" % (fcode.co_code, fcode.co_consts)).hexdigest()

class BaseModel(DBModel):
    #def __init__(self, parent=None, key_name=None, _app=None, **kwds):
    #    DBModel.__init__(self, parent=None, key_name=None, _app=None, **kwds)

    def put(self, **kw):
        if not self.is_saved():
            tname = "tablecounter_%s" % (self.__class__.__name__ , )
            tval = Setting.get(tname, useMemoryCache=False)
            if tval == None:
                tval = self.__class__.count(None)
            Setting.set(tname, tval + 1, False)
        super(BaseModel, self).put(**kw)

    def delete(self, **kw):
        if self.is_saved():
            tname = "tablecounter_%s" % self.__class__.__name__
            tval = Setting.get(tname, useMemoryCache=False)
            if tval == None:
                tval = self.__class__.all().count(None)
            Setting.set(tname, tval - 1, False)
        super(BaseModel, self).delete(**kw)

    @classmethod
    def deletes(cls, vals):
        tname = "tablecounter_%s" % cls.__name__
        tval = Setting.get(tname, useMemoryCache=False)
        if tval == None:
            tval = cls.all().count(None)
        Setting.set(tname, tval - len(vals), False)

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
        results = cls.all().fetch(plen, offset) if fun is None else fun(cls.all()).fetch(plen, offset)
        return _Pager(results, total, p, n)

    @classmethod
    def total(cls, func=None):
        if func:
            tname = "tablecounter_%s::%s" % (cls.__name__, func2str(func)) 
        else:
            tname = "tablecounter_%s" % (cls.__name__)

        tval = Setting.get(tname, useMemoryCache=False)
        if tval == None:
            logging.info("calc the %s total count" % cls.__name__)
            tval = cls.all().count(None) if fun == None else fun(cls.all()).count(None)
            Setting.set(tname, tval, False)
        return tval
